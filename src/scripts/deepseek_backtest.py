"""
DeepSeek Backtest Implementation
Uses VWAP and volume analysis for trading decisions.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

class DeepSeekBacktest(Strategy):
    def init(self):
        self.vwap = self.I(talib.SMA, self.data.Close * self.data.Volume, timeperiod=20)
        self.volume = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        print("VWAP and Volume calculations initialized successfully!")
        
    def next(self):
        if not self.position:
            if self.data.Close[-1] > self.vwap[-1]:
                self.buy()
                print("Long position entered!")
            elif self.data.Close[-1] < self.vwap[-1]:
                self.sell()
                print("Short position entered!")

# Load data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
print("Loading data from:", data_path)
data = pd.read_csv(data_path)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Initialize and run backtest
bt = Backtest(data, DeepSeekBacktest, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)

# Save initial performance chart
strategy_name = "DeepSeekBacktest"
chart_dir = str(Path(__file__).parent.parent / "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print(f"Saving initial chart to: {chart_file}")
bt.plot(filename=chart_file, open_browser=False)

print("Backtest completed successfully!")
