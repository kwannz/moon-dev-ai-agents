"""
API Handler
Manages API interactions and data caching
"""

import os
import sys
import time
import json
from pathlib import Path
import pandas as pd
import requests
from termcolor import cprint

class APIHandler:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('API_KEY')
        self.base_dir = Path(__file__).parent.parent / "data" / "cache"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        print("API Handler: Ready to process requests")
        print(f"Cache directory: {self.base_dir.absolute()}")
        
    def _fetch_cached_data(self, filename, limit=None):
        """Fetch data from cache or API"""
        try:
            print(f"Fetching {filename}{'with limit '+str(limit) if limit else ''}...")
            
            cache_file = self.base_dir / filename
            if cache_file.exists():
                data = pd.read_csv(cache_file)
                if limit:
                    data = data.head(limit)
                return data
                
            return self._fetch_from_api(filename, limit)
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def _fetch_from_api(self, endpoint, limit=None):
        """Fetch data from API"""
        if not self.api_key:
            print("Error: API key not found")
            return None
            
        try:
            response = requests.get(
                f"https://api.example.com/{endpoint}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"limit": limit} if limit else None
            )
            response.raise_for_status()
            return pd.DataFrame(response.json())
            
        except Exception as e:
            print(f"API error: {e}")
            return None

    def get_market_data(self, symbol, limit=None):
        """Get market data for a symbol"""
        return self._fetch_cached_data(f"market_{symbol}.csv", limit)

    def get_funding_data(self, symbol, limit=None):
        """Get funding rate data for a symbol"""
        return self._fetch_cached_data(f"funding_{symbol}.csv", limit)

if __name__ == "__main__":
    print("API Handler Test Suite")
    print("=" * 50)
    
    api = APIHandler()
    
    # Test market data
    btc_data = api.get_market_data("BTC", limit=5)
    if btc_data is not None:
        print("\nBTC Market Data:")
        print(btc_data)
    
    # Test funding data
    eth_funding = api.get_funding_data("ETH", limit=5)
    if eth_funding is not None:
        print("\nETH Funding Data:")
        print(eth_funding)
    
    print("\nAPI Handler Test Complete!")
    print("\nNote: Make sure to set API_KEY in your .env file")
