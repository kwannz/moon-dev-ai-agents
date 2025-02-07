"""
AtrReversion strategy implementation using TA-Lib indicators.
Uses ATR-based mean reversion for trading decisions.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

class AtrReversion(Strategy):
    def init(self):
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
    def next(self):
        if not self.position:
            if self.data.Close[-1] < self.data.Close[-2] - self.atr[-1]:
                self.buy()
        else:
            if self.data.Close[-1] > self.data.Close[-2] + self.atr[-1]:
                self.position.close()

# Load data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
print("Loading data from:", data_path)
data = pd.read_csv(data_path)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Initialize and run backtest
bt = Backtest(data, AtrReversion, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)

# Save initial performance chart
strategy_name = "AtrReversion"
chart_dir = str(Path(__file__).parent.parent / "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print(f"Saving initial chart to: {chart_file}")
bt.plot(filename=chart_file, open_browser=False)

print("Backtest completed successfully!")
