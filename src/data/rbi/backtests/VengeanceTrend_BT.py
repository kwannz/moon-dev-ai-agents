#!/usr/bin/env python3
"""
Lumix Backtest AI - VengeanceTrend Strategy
This implementation includes all necessary components:
- Trend following with ATR-based trailing stops
- Risk management and position sizing
- Parameter optimization
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

class VengeanceTrend(Strategy):
    # Strategy parameters
    atr_period = 14
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        """Initialize strategy indicators"""
        print("✨ Initializing indicators...")
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                         self.data.Close, timeperiod=self.atr_period)
        self.trailing_stop_long = float('-inf')
        self.trailing_stop_short = float('inf')
        
    def next(self):
        """Execute trading logic for the current candle"""
        atr_value = self.atr[-1]
        
        # Update trailing stops for open positions
        if self.position.is_long:
            self.trailing_stop_long = max(self.trailing_stop_long, self.data.Low[-1] - 2 * atr_value)
            if self.data.Close[-1] < self.trailing_stop_long:
                self.position.close()
                print(f"✨ Long position closed! Price: {self.data.Close[-1]}, Trailing Stop: {self.trailing_stop_long}")
        
        elif self.position.is_short:
            self.trailing_stop_short = min(self.trailing_stop_short, self.data.High[-1] + 2 * atr_value)
            if self.data.Close[-1] > self.trailing_stop_short:
                self.position.close()
                print(f"✨ Short position closed! Price: {self.data.Close[-1]}, Trailing Stop: {self.trailing_stop_short}")

# Load data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
data = pd.read_csv(data_path, parse_dates=['datetime'])
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Initialize and run backtest
bt = Backtest(data, VengeanceTrend, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n✨ Initial Backtest Stats:")
print(stats)

# Save initial plot
chart_file = os.path.join(str(Path(__file__).parent.parent / "charts"), "VengeanceTrend_initial_chart.html")
bt.plot(filename=chart_file, open_browser=False)
print(f"✨ Initial plot saved to {chart_file}")

# Optimize parameters
optimization_results = bt.optimize(
    atr_period=range(10, 21),
    risk_per_trade=[0.01, 0.02],
    maximize='Return [%]'
)
print("✨ Optimization Results:")
print(optimization_results)

# Save optimized plot
optimized_chart_file = os.path.join(str(Path(__file__).parent.parent / "charts"), "VengeanceTrend_optimized_chart.html")
bt.plot(filename=optimized_chart_file, open_browser=False)
print(f"✨ Optimized plot saved to {optimized_chart_file}")

print("✨ Backtest completed successfully!")
