"""
CoinGecko Token Finder
Finds Solana tokens that aren't listed on major exchanges.
"""

import os
import requests
import json
from pathlib import Path

class TokenFinder:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "X-CG-API-Key": self.api_key
        }
        self.api_calls = 0
        print("CoinGecko Token Finder initialized!")

print("Token Finder initialized successfully!")
