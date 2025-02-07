"""
Chart Analysis Agent
Analyzes trading charts and provides technical analysis
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import talib
from termcolor import cprint

class ChartAnalysisAgent:
    def __init__(self, model=None):
        self.model = model
        self.timeframes = {
            "1m": "1-minute",
            "5m": "5-minute",
            "15m": "15-minute",
            "1h": "1-hour",
            "4h": "4-hour",
            "1d": "daily"
        }
        
    def analyze_chart(self, symbol, timeframe):
        """Analyze chart for given symbol and timeframe"""
        current_price = self.data.Close[-1]
        sma_20 = talib.SMA(self.data.Close, timeperiod=20)[-1]
        sma_50 = talib.SMA(self.data.Close, timeperiod=50)[-1]
        rsi = talib.RSI(self.data.Close, timeperiod=14)[-1]
        
        analysis = {
            "direction": "bullish" if current_price > sma_20 else "bearish",
            "analysis": self._generate_analysis(current_price, sma_20, sma_50, rsi)
        }
        
        friendly_timeframe = self.timeframes.get(timeframe, timeframe)
        message = (
            f"Chart analysis for {symbol} on the {friendly_timeframe} timeframe! "
            f"The trend is {analysis['direction']}. {analysis['analysis']} "
        )
        
        return message

    def _generate_analysis(self, price, sma_20, sma_50, rsi):
        """Generate technical analysis message"""
        if price > sma_20 and price > sma_50:
            return "Strong uptrend with price above both moving averages."
        elif price < sma_20 and price < sma_50:
            return "Strong downtrend with price below both moving averages."
        else:
            return "Mixed signals - price between moving averages."

    def run(self):
        """Main loop for chart analysis"""
        print("\nChart Analysis Agent Starting Up...")
        print("Ready to analyze charts! 📊")
        
        try:
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nChart Analysis Agent shutting down...")

if __name__ == "__main__":
    agent = ChartAnalysisAgent()
    agent.run()
