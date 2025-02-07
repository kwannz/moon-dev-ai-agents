from typing import Dict, List, Optional, Tuple
import requests
import json
import os
import time
from datetime import datetime, timedelta
import pandas as pd
from termcolor import cprint
import websockets
import asyncio
from dotenv import load_dotenv

class HeliusClient:
    """Client for interacting with Helius API"""
    
    def __init__(self):
        """Initialize Helius client with API key from environment"""
        load_dotenv()
        self.api_key = os.getenv("HELIUS_API_KEY")
        if not self.api_key:
            raise ValueError("HELIUS_API_KEY environment variable is required")
        self.base_url = f"https://mainnet.helius-rpc.com/?api-key={self.api_key}"
        self.ws_url = f"wss://mainnet.helius-rpc.com/?api-key={self.api_key}"
        self.parse_tx_url = f"https://api.helius.xyz/v0/transactions/?api-key={self.api_key}"
        self.parse_tx_history_url = f"https://api.helius.xyz/v0/addresses/{{address}}/transactions/?api-key={self.api_key}"
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
        
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
        
    def get_token_price(self, token_address: str) -> float:
        """Get current token price using DAS API"""
        self._rate_limit()
        try:
            response = requests.post(
                f"{self.base_url}",
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": "get-token-data",
                    "method": "searchAssets",
                    "params": {
                        "ownerAddress": token_address,
                        "tokenType": "fungible"
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            if "result" in data and data["result"]:
                return float(data["result"][0].get("price", 0))
            return 0.0
        except Exception as e:
            cprint(f"❌ Failed to get token price: {str(e)}", "red")
            return 0.0
            
    def get_token_data(self, token_address: str, days_back: int = 3, timeframe: str = '1H') -> pd.DataFrame:
        """Get historical token data and format as OHLCV"""
        try:
            self._rate_limit()
            # Get token data using getAssetBatch
            response = requests.post(
                f"{self.base_url}",
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": "get-token-data",
                    "method": "getAssetBatch",
                    "params": {
                        "ids": [token_address],
                        "options": {
                            "showRecentTrades": True,
                            "showMetadata": True
                        }
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("result"):
                raise ValueError("No data returned from Helius API")
                
            token_data = data["result"][0]
            current_price = float(token_data.get("price", 0))
            volume = float(token_data.get("volume24h", 0))
            
            # Create DataFrame with current data
            now = datetime.now()
            df = pd.DataFrame({
                'Datetime (UTC)': [now.strftime('%Y-%m-%d %H:%M:%S')],
                'Open': [current_price],
                'High': [current_price],
                'Low': [current_price],
                'Close': [current_price],
                'Volume': [volume]
            })
            
            # Add technical indicators
            if len(df) >= 20:
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['RSI'] = self._calculate_rsi(df['Close'])
            if len(df) >= 40:
                df['MA40'] = df['Close'].rolling(window=40).mean()
                df['Price_above_MA20'] = df['Close'] > df['MA20']
                df['Price_above_MA40'] = df['Close'] > df['MA40']
                df['MA20_above_MA40'] = df['MA20'] > df['MA40']
                
            return df
        except Exception as e:
            cprint(f"❌ Failed to get token data: {str(e)}", "red")
            return pd.DataFrame()
            
    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate RSI for a price series"""
        deltas = prices.diff()
        gain = (deltas.where(deltas.gt(0), 0)).rolling(window=periods).mean()
        loss = (-deltas.where(deltas.lt(0), 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    async def subscribe_token_updates(self, token_address: str, callback) -> None:
        """Subscribe to token updates using WebSocket"""
        while True:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    subscribe_msg = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "accountSubscribe",
                        "params": [token_address]
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    
                    # Health check task
                    async def health_check():
                        while True:
                            try:
                                await websocket.ping()
                                await asyncio.sleep(60)
                            except Exception:
                                break
                                
                    health_task = asyncio.create_task(health_check())
                    
                    while True:
                        try:
                            msg = await websocket.recv()
                            data = json.loads(msg)
                            await callback(data)
                        except Exception as e:
                            cprint(f"❌ WebSocket error: {str(e)}", "red")
                            break
                            
                    health_task.cancel()
                    
            except Exception as e:
                cprint(f"❌ WebSocket connection error: {str(e)}", "red")
                await asyncio.sleep(5)  # Wait before reconnecting
                
    async def collect_ohlcv_data(self, token_address: str, callback) -> None:
        """Collect OHLCV data using WebSocket and DAS API
        
        Args:
            token_address: Token mint address
            callback: Async function to handle price updates
        """
        while True:
            try:
                # Get initial token data
                df = self.get_token_data(token_address)
                if df is not None and not df.empty:
                    await callback(df)
                
                # Subscribe to real-time updates
                await self.subscribe_token_updates(token_address, callback)
                
            except Exception as e:
                cprint(f"❌ OHLCV collection error: {str(e)}", "red")
                await asyncio.sleep(5)  # Wait before retrying
