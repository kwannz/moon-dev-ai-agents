"""
Lumix OHLCV Data Collector
Collects Open-High-Low-Close-Volume data for specified tokens
"""

from src.config import *
import pandas as pd
from datetime import datetime
import os
from termcolor import colored, cprint
import time
from src.data.helius_client import HeliusClient
from src.config import LOOKBACK_DAYS, TIMEFRAME, SAVE_MARKET_DATA

def collect_token_data(token, days_back=LOOKBACK_DAYS, timeframe=TIMEFRAME):
    """Collect OHLCV data for a single token"""
    cprint(f"\n🤖 Lumix AI Agent fetching data for {token}...", "white", "on_blue")
    
    try:
        # Check temp data first
        temp_file = f"temp_data/{token}_latest.csv"
        if os.path.exists(temp_file):
            print(f"📂 Found cached data for {token[:4]}")
            return pd.read_csv(temp_file)
            
        # Get data from Helius
        try:
            client = HeliusClient()
            data = client.get_token_data(token, days_back, timeframe)
        except Exception as e:
            cprint(f"❌ Failed to initialize Helius client: {str(e)}", "white", "on_red")
            return None
        
        if data is None or data.empty:
            cprint(f"❌ AI Agent couldn't fetch data for {token}", "white", "on_red")
            return None
            
        cprint(f"📊 AI Agent processed {len(data)} candles for analysis", "white", "on_blue")
        
        # Save data if configured
        if SAVE_OHLCV_DATA:
            save_path = f"data/{token}_latest.csv"
        else:
            save_path = f"temp_data/{token}_latest.csv"
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save to CSV
        data.to_csv(save_path)
        cprint(f"💾 AI Agent cached data for {token[:4]}", "white", "on_green")
        
        return data
        
    except Exception as e:
        cprint(f"❌ AI Agent encountered an error: {str(e)}", "white", "on_red")
        return None

def collect_all_tokens():
    """Collect OHLCV data for all monitored tokens"""
    market_data = {}
    
    cprint("\n🔍 AI Agent starting market data collection...", "white", "on_blue")
    
    for token in MONITORED_TOKENS:
        data = collect_token_data(token)
        if data is not None:
            market_data[token] = data
            
    cprint("\n✨ AI Agent completed market data collection!", "white", "on_green")
    
    return market_data

if __name__ == "__main__":
    try:
        collect_all_tokens()
    except KeyboardInterrupt:
        print("\n👋 Lumix OHLCV Collector shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("🔧 Please check the logs and try again!")            