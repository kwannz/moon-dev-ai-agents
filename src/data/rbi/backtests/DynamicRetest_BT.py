#!/usr/bin/env python3
"""
Lumix Backtest AI - Dynamic Retest Strategy Backtesting & Optimization
----------------------------------------------------------------------
This script implements the "Dynamic Retest" strategy using backtesting.py.
It includes:
  • Proper risk management with fixed risk per trade
  • Parameter optimization for risk-reward ratio and risk percentage
  • Position sizing based on equity and risk amount
  • Charts saved to the specified "charts" directory
Enjoy backtesting! ✨
"""

import os
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

class DynamicRetest(Strategy):
    def init(self):
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20)
        print("✨ INIT complete – indicators (zone_top, zone_bottom, sma20) are online!")

    def next(self):
        current_open = self.data.Open[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_close = self.data.Close[-1]

        # Debug print – current bar info
        print(f"✨ Processing bar {self.data.index[-1]} → Open: {current_open:.2f}, High: {current_high:.2f}, Low: {current_low:.2f}, Close: {current_close:.2f}")
        print(f"Debug: Consolidation zone [Top: {curr_zone_top:.2f} | Bottom: {curr_zone_bottom:.2f}] over last {self.consolidation_span} bars.")

        # Determine market structure: Basic trend identification using last 3 bars
        try:
            if current_close > self.data.Close[-2] > self.data.Close[-3]:
                trend = 'uptrend'
            elif current_close < self.data.Close[-2] < self.data.Close[-3]:
                trend = 'downtrend'
            else:
                trend = 'none'
        except Exception as e:
            trend = 'none'
        print(f"✨ Trend identified as {trend.upper()}!")

        # Only consider new trades if not already in a position
        if self.position:
            print("✨ Currently in a trade – holding position!")
            return

        # Entry logic for long trades
        if trend == 'uptrend':
            if curr_zone_bottom < current_close <= curr_zone_top:
                risk = current_close - curr_zone_bottom  # Risk per unit for a long trade
                if risk <= 0:
                    print("✨ Calculated risk for LONG trade is non-positive. Skipping...")
                    return
                if eff_risk_reward < 2.5:
                    print("✨ Effective risk/reward ratio below 2.5:1 for LONG. Aborting trade!")
                    return
                potential_reward = risk * eff_risk_reward
                take_profit = current_close + potential_reward

                # Validate that the recent high is high enough to reach our TP target
                recent_high = self.data.High[-self.consolidation_span:].max()
                if take_profit > current_close + (2 * recent_range):
                    print(f"✨ TP target ({take_profit:.2f}) too far from current price. LONG trade skipped!")
                    return

                # Calculate dynamic position size based on risk percentage
                risk_amount = self.equity * eff_risk_percent
                position_size = int(risk_amount / risk)

                # Set stop loss just below the demand zone (a slight buffer)
                stop_loss = curr_zone_bottom * 0.999

                print(f"✨ LONG signal detected! Entry = {current_close:.2f}, Stop Loss = {stop_loss:.2f}, Take Profit = {take_profit:.2f}, Size = {position_size}")
                self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                return

        # Entry logic for short trades
        elif trend == 'downtrend':
            if curr_zone_bottom <= current_close < curr_zone_top:
                risk = curr_zone_top - current_close  # Risk per unit for a short trade
                if risk <= 0:
                    print("✨ Calculated risk for SHORT trade is non-positive. Skipping...")
                    return
                if eff_risk_reward < 2.5:
                    print("✨ Effective risk/reward ratio below 2.5:1 for SHORT. Aborting trade!")
                    return
                potential_reward = risk * eff_risk_reward
                take_profit = current_close - potential_reward

                # Ensure that the recent low is low enough to allow our target hit
                recent_low = self.data.Low[-self.consolidation_span:].min()
                if take_profit < current_close - (2 * recent_range):
                    print(f"✨ TP target ({take_profit:.2f}) too far from current price. SHORT trade skipped!")
                    return

                risk_amount = self.equity * eff_risk_percent
                position_size = int(risk_amount / risk)

                # Place stop loss just above the supply zone, with a small buffer
                stop_loss = curr_zone_top * 1.001

                print(f"✨ SHORT signal detected! Entry = {current_close:.2f}, Stop Loss = {stop_loss:.2f}, Take Profit = {take_profit:.2f}, Size = {position_size}")
                self.sell(size=position_size, sl=stop_loss, tp=take_profit)
                return

        # If no signal was generated, log it!
        print("✨ No valid trade signal on this bar. Scanning for the perfect setup...")

# Load and prepare data
data = pd.read_csv(DATA_PATH)
data.columns = data.columns.str.strip().str.lower()
unnamed_cols = [col for col in data.columns if 'unnamed' in col.lower()]
if unnamed_cols:
    data = data.drop(columns=unnamed_cols)
    print("✨ Dropped unnamed columns:", unnamed_cols)

# Initialize and run backtest
bt = Backtest(data, DynamicRetest, cash=1_000_000, commission=0.0, exclusive_orders=True)
stats = bt.run()
print("✨ Initial Backtest Stats:")
print(stats)
print("✨ Strategy Parameters:")
print(stats._strategy)

# Save initial performance plot
strategy_name = "Dynamic_Retest"
chart_dir = os.path.join(BASE_DIR, "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print(f"✨ Saving initial performance plot to {chart_file}")
bt.plot(filename=chart_file, open_browser=False)

# Parameter optimization
print("✨ Starting parameter optimization...")
optimized_stats = bt.optimize(risk_reward=range(25, 31, 1),          # Effective risk_reward: 2.5:1 to 3.0:1
                          risk_percent=range(1, 3, 1),            # 1% to 2% risk per trade
                          consolidation_span=range(2, 6),         # Consolidation span from 2 to 5 bars
                          maximize='Equity Final [$]',
                          return_heatmap=False)

print("✨ Optimization complete!")
print("✨ Optimized Stats:")
print(optimized_stats)

# Save optimized performance plot
opt_chart_file = os.path.join(chart_dir, f"{strategy_name}_optimized_chart.html")
print(f"✨ Saving optimized performance plot to {opt_chart_file}")
bt.plot(filename=opt_chart_file, open_browser=False)

print("✨ All done! Happy backtesting!")
