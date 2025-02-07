"""
CoinGecko API Examples
All API endpoints with easy toggle functionality
"""

import os
import requests
import json
from pathlib import Path

class CoinGeckoExamples:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "X-CG-API-Key": self.api_key
        }
        self.endpoints = {
            "ping": "/ping",
            "simple_price": "/simple/price",
            "coins_list": "/coins/list",
            "coins_markets": "/coins/markets"
        }
        print("CoinGecko Examples Initialized!")

print("API integration initialized successfully!")
