"""
StochasticPhaseFilter strategy implementation using TA-Lib indicators.
Uses stochastic oscillator phases for trading decisions.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

class StochasticPhaseFilter(Strategy):
    def init(self):
        self.stoch_k, self.stoch_d = self.I(talib.STOCH, self.data.High, self.data.Low, self.data.Close)
        
    def next(self):
        if not self.position:
            if self.stoch_k[-1] < 20 and self.stoch_d[-1] < 20:
                self.buy()
        else:
            if self.stoch_k[-1] > 80 and self.stoch_d[-1] > 80:
                self.position.close()

# Load data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
print("Loading data from:", data_path)
data = pd.read_csv(data_path)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Initialize and run backtest
bt = Backtest(data, StochasticPhaseFilter, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)

# Save initial performance chart
strategy_name = "StochasticPhaseFilter"
chart_dir = str(Path(__file__).parent.parent / "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print(f"Saving initial chart to: {chart_file}")
bt.plot(filename=chart_file, open_browser=False)

print("Backtest completed successfully!")
