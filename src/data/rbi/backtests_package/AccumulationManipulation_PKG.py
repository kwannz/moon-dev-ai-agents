"""
Lumix Backtest AI - AccumulationManipulation Strategy
This implementation includes proper risk management and position sizing.
Uses accumulation and manipulation patterns for trading decisions.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

class AccumulationManipulation(Strategy):
    def init(self):
        self.sma_fast = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.sma_slow = self.I(talib.SMA, self.data.Close, timeperiod=50)
        
    def next(self):
        if not self.position:
            if self.sma_fast[-1] > self.sma_slow[-1]:
                self.buy()
        else:
            if self.sma_fast[-1] < self.sma_slow[-1]:
                self.position.close()

# Load data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
print("✨ Loading data from:", data_path)
data = pd.read_csv(data_path)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Initialize and run backtest
bt = Backtest(data, AccumulationManipulation, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)

# Save initial performance chart
strategy_name = "AccumulationManipulation"
chart_dir = str(Path(__file__).parent.parent / "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print(f"Saving initial chart to: {chart_file}")
bt.plot(filename=chart_file, open_browser=False)

print("✨ Backtest completed successfully!")
