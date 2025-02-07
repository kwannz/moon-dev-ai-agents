"""
Risk Agent
Monitors and manages trading risk
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from termcolor import cprint
from src.agents.focus_agent import MODEL_TYPE, MODEL_NAME
from src.models import ModelFactory

class RiskAgent:
    def __init__(self, model_type=MODEL_TYPE, model_name=MODEL_NAME):
        self.model_type = model_type
        self.model_name = model_name
        self.model_factory = ModelFactory()
        self.model = self.model_factory.get_model(self.model_type)
        self.min_balance = 50.00
        self.max_position_size = 0.20
        self.cash_buffer = 0.30
        self.slippage = 0.025
        
    def analyze_risk(self, portfolio_data):
        """Analyze portfolio risk"""
        if not portfolio_data or not isinstance(portfolio_data, dict):
            return None
            
        try:
            # Format data for analysis
            context = f"""
            Portfolio Value: ${portfolio_data.get('total_value', 0):.2f}
            Current PnL: ${portfolio_data.get('pnl', 0):.2f}
            Position Sizes: {portfolio_data.get('positions', {})}
            """
            
            if self.model:
                response = self.model.generate_response(
                    system_prompt="You are the Risk Analysis AI. Analyze portfolio risk.",
                    user_content=context,
                    temperature=0.7
                )
                return self._parse_analysis(response)
            else:
                print("Model not initialized")
                return None
                
        except Exception as e:
            print(f"Error analyzing risk: {e}")
            return None

    def run(self):
        """Main monitoring loop"""
        print("\nRisk Agent starting...")
        print("Ready to monitor portfolio risk!")
        
        try:
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nRisk Agent shutting down...")

if __name__ == "__main__":
    agent = RiskAgent()
    agent.run()
