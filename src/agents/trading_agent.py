"""
Trading Agent
Handles automated trading execution and analysis
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from termcolor import cprint
from dotenv import load_dotenv
from src import nice_funcs as n
from src.data.ohlcv_collector import collect_all_tokens
from src.agents.focus_agent import MODEL_TYPE, MODEL_NAME
from src.models import ModelFactory

# Load environment variables
load_dotenv()

class TradingAgent:
    def __init__(self, model_type=MODEL_TYPE, model_name=MODEL_NAME):
        self.model_type = model_type
        self.model_name = model_name
        self.model_factory = ModelFactory()
        self.model = self.model_factory.get_model(self.model_type)
        self.min_trade_size = 0.01
        self.max_position_size = 0.20
        self.cash_buffer = 0.30
        self.slippage = 0.025
        
    def analyze_market_data(self, token_data):
        """Analyze market data for trading opportunities"""
        if not token_data or not isinstance(token_data, dict):
            return None
            
        try:
            # Format data for analysis
            context = f"""
            Token: {token_data.get('symbol')}
            Price: {token_data.get('price')}
            Volume: {token_data.get('volume')}
            Market Cap: {token_data.get('market_cap')}
            """
            
            if self.model:
                response = self.model.generate_response(
                    system_prompt="You are the Trading Analysis AI. Analyze market data.",
                    user_content=context,
                    temperature=0.7
                )
                return self._parse_analysis(response)
            else:
                print("Model not initialized")
                return None
                
        except Exception as e:
            print(f"Error analyzing market data: {e}")
            return None

    def run(self):
        """Main processing loop"""
        print("\nTrading Agent starting...")
        print("Ready to analyze market data!")
        
        try:
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nTrading Agent shutting down...")

if __name__ == "__main__":
    agent = TradingAgent()
    agent.run()
