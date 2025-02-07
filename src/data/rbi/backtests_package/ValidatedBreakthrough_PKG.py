"""
ValidatedBreakthrough strategy implementation using TA-Lib indicators.
Uses breakout validation for trading decisions.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

class ValidatedBreakthrough(Strategy):
    sma_period = 20
    lookback = 10
    
    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period)
        self.recent_high = self.I(talib.MAX, self.data.High, timeperiod=self.lookback)
        self.recent_low = self.I(talib.MIN, self.data.Low, timeperiod=self.lookback)
        print(f"Indicators initialized: SMA period = {self.sma_period}, Lookback = {self.lookback}")
    
    def next(self):
        current_price = self.data.Close[-1]
        print(f"New bar processed – Current Price: {current_price:.2f}")
        
        if not self.position:
            if current_price > self.sma[-1]:
                print(f"Uptrend detected – Close {current_price:.2f} > SMA {self.sma[-1]:.2f}")
                if current_price < self.recent_low[-1] * 1.02:
                    self.buy()
        else:
            if current_price < self.sma[-1]:
                self.position.close()

# Load data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
print("Loading data from:", data_path)
data = pd.read_csv(data_path)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Initialize and run backtest
bt = Backtest(data, ValidatedBreakthrough, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)

# Save initial performance chart
strategy_name = "ValidatedBreakthrough"
chart_dir = str(Path(__file__).parent.parent / "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print(f"Saving initial chart to: {chart_file}")
bt.plot(filename=chart_file, open_browser=False)

print("Backtest completed successfully!")
