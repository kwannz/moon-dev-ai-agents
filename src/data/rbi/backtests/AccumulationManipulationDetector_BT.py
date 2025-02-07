"""
AccumulationManipulationDetector strategy implementation using TA-Lib indicators.
Detects accumulation and manipulation patterns in price action.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Data Handling
print("Loading data from CSV...")
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
data = pd.read_csv(data_path)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Map columns to proper case for backtesting
column_mapping = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'datetime'
}
data = data[list(column_mapping.keys())]
data = data.rename(columns=column_mapping)

data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

class AccumulationManipulationDetector(Strategy):
    risk_percent = 1.0
    risk_reward = 200
    
    def init(self):
        self.sma_short = self.I(talib.SMA, self.data.Close, timeperiod=9)
        self.sma_long = self.I(talib.SMA, self.data.Close, timeperiod=21)
    
    def next(self):
        current_time = self.data.index[self.bar_index].time()
        start_time = pd.Timestamp("10:00").time()
        end_time = pd.Timestamp("11:30").time()
        
        if not (start_time <= current_time <= end_time):
            return
        
        bullish_bias = self.sma_short[-1] > self.sma_long[-1]
        
        if not self.position:
            recent_ranges = self.data.High[-5:] - self.data.Low[-5:]
            avg_range = np.mean(recent_ranges)
            recent_max_range = np.max(self.data.High[-3:] - self.data.Low[-3:])
            
            if recent_max_range > 1.2 * avg_range:
                return
            
            fair_value_gap = self.data.Open[-2]
            if bullish_bias and (self.data.Close[-1] <= fair_value_gap * 1.01):
                stop_loss = self.data.Low[-2]
                entry_price = self.data.Close[-1]
                risk = entry_price - stop_loss
                if risk <= 0:
                    return
                    
                risk_amount = self.equity * (self.risk_percent / 100)
                position_size = int(round(risk_amount / risk))
                if position_size <= 0:
                    return
                    
                take_profit = entry_price + risk * (self.risk_reward / 100)
                self.buy(size=position_size, sl=stop_loss, tp=take_profit)

# Initialize and run backtest
bt = Backtest(data, AccumulationManipulationDetector, cash=1_000_000, commission=.000, exclusive_orders=True)
stats = bt.run()
print(stats)
print(stats._strategy)

# Save initial performance chart
strategy_name = "AccumulationManipulationDetector"
chart_dir = str(Path(__file__).parent.parent / "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print(f"Saving initial chart to {chart_file}")
bt.plot(filename=chart_file, open_browser=False)

# Optimization
print("Starting parameter optimization...")
optim = bt.optimize(risk_reward=range(150, 251, 50),
                   maximize='Equity Final [$]',
                   constraint=lambda param: param.risk_reward > 0,
                   return_stats=True)

print("Optimization complete!")
print(optim)
print(optim._strategy)

# Save optimized chart
opt_chart_file = os.path.join(chart_dir, f"{strategy_name}_optimized_chart.html")
print(f"Saving optimized chart to {opt_chart_file}")
bt.plot(filename=opt_chart_file, open_browser=False)

print("Backtest completed successfully!")
