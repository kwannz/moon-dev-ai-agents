"""
DeepSeek API integration for real-time trading.
"""

import os
import requests
import time
from pathlib import Path

MAX_RETRIES = 3
RETRY_DELAY = 5

def call_deepseek_api(prompt, model="deepseek-r1:1.5b", temperature=0.7, max_tokens=1000):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Please check the API status.")
                return None

print("API integration initialized successfully!")
