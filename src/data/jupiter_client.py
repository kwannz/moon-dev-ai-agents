from typing import Dict, Optional
import requests
import json
import time
import os
from termcolor import cprint
from solders.keypair import Keypair
from solana.rpc.types import TxOpts
from dotenv import load_dotenv

load_dotenv()

class JupiterClient:
    def __init__(self):
        self.base_url = "https://quote-api.jup.ag/v6"
        self.headers = {"Content-Type": "application/json"}
        self.slippage_bps = 250  # 2.5% slippage
        self.max_retries = 3
        self.retry_delay = 1000  # 1 second initial delay
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
        
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
        
    def get_quote(self, input_mint: str, output_mint: str, amount: int) -> Optional[Dict]:
        """Get quote for token swap"""
        try:
            self._rate_limit()
            url = f"{self.base_url}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "slippageBps": self.slippage_bps,
                "maxAccounts": 54
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            cprint(f"❌ Failed to get quote: {str(e)}", "red")
            return None
            
    def execute_swap(self, quote_response: Dict, wallet_pubkey: str) -> Optional[str]:
        """Execute swap transaction using Jupiter API"""
        try:
            self._rate_limit()
            url = f"{self.base_url}/swap"
            payload = {
                "quoteResponse": quote_response,
                "userPublicKey": wallet_pubkey,
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": {
                    "priorityLevelWithMaxLamports": {
                        "maxLamports": 10000000,
                        "priorityLevel": "veryHigh"
                    }
                },
                "dynamicComputeUnitLimit": True
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("swapTransaction")
        except Exception as e:
            cprint(f"❌ Failed to execute swap: {str(e)}", "red")
            return None
            
    def monitor_transaction(self, signature: str, max_retries: int = 5) -> bool:
        """Monitor transaction status with exponential backoff"""
        try:
            retry_count = 0
            delay = 1.0  # Initial delay in seconds
            
            while retry_count < max_retries:
                self._rate_limit()
                response = requests.post(
                    f"https://mainnet.helius-rpc.com/?api-key={os.getenv('HELIUS_API_KEY')}",
                    headers=self.headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": "get-tx-status",
                        "method": "getSignatureStatuses",
                        "params": [[signature]]
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if "result" in data and data["result"]["value"][0]:
                    status = data["result"]["value"][0]
                    if status.get("confirmationStatus") == "finalized":
                        cprint(f"✅ Transaction {signature[:8]}... confirmed", "green")
                        return True
                    elif status.get("err"):
                        cprint(f"❌ Transaction {signature[:8]}... failed: {status['err']}", "red")
                        return False
                
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                
            cprint(f"❌ Transaction {signature[:8]}... timed out after {max_retries} retries", "red")
            return False
            
        except Exception as e:
            cprint(f"❌ Transaction monitoring failed: {str(e)}", "red")
            return False
