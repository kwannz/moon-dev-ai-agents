#!/usr/bin/env python3
"""
Lumix Backtest AI - DynamicValidation Strategy Backtest Implementation

This implementation of the "DynamicValidation" strategy focuses on market structure,
supply and demand, and risk management using dynamic validation of lows and highs.
It uses TA‐Lib indicators through the self.I wrapper, with detailed logging ✨
"""

from pathlib import Path
import os
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Data Handling & Preparation
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "BTC-USD-15m.csv"

# Read CSV and clean data columns
print("✨ Loading data from:", DATA_PATH)
data = pd.read_csv(DATA_PATH)

# Clean column names and ensure proper OHLCV format
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Ensure we have all required columns
required_cols = ['open', 'high', 'low', 'close', 'volume']
if not all(col in data.columns for col in required_cols):
    raise ValueError(f"Missing required columns. Found: {data.columns.tolist()}")

# Map columns to match backtesting requirements
col_mapping = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'Datetime'
}
data.rename(columns=col_mapping, inplace=True)

# Parse datetime and set as index
if 'Datetime' in data.columns:
    data['Datetime'] = pd.to_datetime(data['Datetime'])
    data.set_index('Datetime', inplace=True)

# Sort index and drop any duplicates
data = data.sort_index()
data = data[~data.index.duplicated(keep='first')]

# Drop any rows with NaN values
data = data.dropna()

print("✨ Data shape after cleaning:", data.shape)
print("✨ Data head preview:")
print(data.head())
print("✨ Data preparation complete.\n")

# Strategy Definition: DynamicValidation
class DynamicValidation(Strategy):
    # Default parameters
    swing_period = 20
    risk_reward_ratio = 3

    def init(self):
        print("✨ Initializing DynamicValidation strategy...")
        self.demand_zone = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period)
        self.supply_zone = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period)
        self.sma50 = self.I(talib.SMA, self.data.Close, timeperiod=50)

    def next(self):
        if len(self.data.Close) < self.swing_period:
            return

        # Only take new positions if we don't have any open positions
        if not self.position:
            # LONG setup
            if self.data.Close[-1] <= self.demand_zone[-1] * 1.01:
                stop_loss = self.demand_zone[-1] * 0.999  # Slightly below demand zone
                entry_price = self.data.Close[-1]
                risk = entry_price - stop_loss

                if risk > 0:
                    risk_amount = self.equity * 0.02  # 2% risk per trade
                    position_size = max(1, int(risk_amount / risk))  # Ensure minimum size of 1
                    take_profit = entry_price + (risk * self.risk_reward_ratio)

                    self.buy(
                        size=position_size, 
                        sl=stop_loss,
                        tp=take_profit
                    )
                    print(f"✨ LONG Entry: Price={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}, Size={position_size}")

            # SHORT setup
            elif self.data.Close[-1] >= self.supply_zone[-1] * 0.99:
                stop_loss = self.supply_zone[-1] * 1.001  # Slightly above supply zone
                entry_price = self.data.Close[-1]
                risk = stop_loss - entry_price

                if risk > 0:
                    risk_amount = self.equity * 0.02  # 2% risk per trade
                    position_size = max(1, int(risk_amount / risk))  # Ensure minimum size of 1
                    take_profit = entry_price - (risk * self.risk_reward_ratio)

                    self.sell(
                        size=position_size,
                        sl=stop_loss,
                        tp=take_profit
                    )
                    print(f"✨ SHORT Entry: Price={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}, Size={position_size}")

# Backtest Execution
if __name__ == '__main__':
    # Create a Backtest instance using DynamicValidation strategy with 1,000,000 initial size.
    bt = Backtest(
        data, 
        DynamicValidation, 
        cash=1000000, 
        commission=0.001,  # 0.1% commission
        margin=1.0,  # No margin
        trade_on_close=True,  # Execute trades on the next candle
        hedging=False,  # No hedging
        exclusive_orders=False  # Allow multiple trades
    )
    strategy_name = "DynamicValidation"
    
    print("\n✨ Running initial backtest with default parameters...")
    stats = bt.run()  
    print("\n✨ Initial Backtest Stats:")
    print(stats)
    print("\n✨ Strategy Parameters:", stats._strategy)
    
    # Save initial performance plot to the charts directory.
    initial_chart_file = os.path.join(str(BASE_DIR / "charts"), f"{strategy_name}_chart.html")
    print("✨ Saving initial performance chart to:", initial_chart_file)
    bt.plot(filename=initial_chart_file, open_browser=False)
    
    # ===============================
    # Parameter Optimization
    # ===============================
    print("\n✨ Starting optimization...")
    # Optimize swing_period and risk_reward_ratio.
    # swing_period is tested across 15, 20, 25, 30
    # risk_reward_ratio is tested across 3, 4, 5
    opt_stats = bt.optimize(
        swing_period=range(15, 35, 5),
        risk_reward_ratio=range(3, 6),
        maximize='Equity Final [$]'  # Removed return_stats parameter
    )
    
    print("\n✨ Optimization complete!")
    print("✨ Optimized Stats:")
    print(opt_stats)
    
    # Re-run backtest using the optimized parameters.
    print("\n✨ Running final backtest with optimized parameters...")
    final_stats = bt.run(
        swing_period=opt_stats._strategy.swing_period,
        risk_reward_ratio=opt_stats._strategy.risk_reward_ratio
    )
    print("\n✨ Final Backtest Stats with optimized parameters:")
    print(final_stats)
    
    # Save final performance plot to the charts directory.
    final_chart_file = os.path.join(str(BASE_DIR / "charts"), f"{strategy_name}_final_chart.html")
    print("✨ Saving final performance chart to:", final_chart_file)
    bt.plot(filename=final_chart_file, open_browser=False)
    
    print("\n✨ Backtesting complete!")
    
# End of file
