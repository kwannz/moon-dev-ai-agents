#!/usr/bin/env python3
"""
Lumix Backtest AI - Dynamic Retest Strategy Backtesting & Optimization
This script implements the "Dynamic Retest" strategy using backtesting.py.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Constants
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "BTC-USD-15m.csv"

class DynamicRetest(Strategy):
    consolidation_span = 20  # Number of bars to look back for consolidation
    eff_risk_reward = 2.5   # Target 2.5:1 reward-to-risk
    eff_risk_percent = 0.01 # Risk 1% per trade
    
    def init(self):
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20)
        print("✨ INIT complete – indicators online!")

    def next(self):
        current_open = self.data.Open[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_close = self.data.Close[-1]

        # Calculate consolidation zone
        lookback = self.data.High[-self.consolidation_span:]
        curr_zone_top = lookback.max()
        curr_zone_bottom = self.data.Low[-self.consolidation_span:].min()
        recent_range = curr_zone_top - curr_zone_bottom

        print(f"✨ Processing bar {self.data.index[-1]} → Open: {current_open:.2f}, High: {current_high:.2f}, Low: {current_low:.2f}, Close: {current_close:.2f}")
        print(f"Debug: Consolidation zone [Top: {curr_zone_top:.2f} | Bottom: {curr_zone_bottom:.2f}] over last {self.consolidation_span} bars.")

        # Determine market structure
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

        if self.position:
            print("✨ Currently in a trade – holding position!")
            return

        # Entry logic for long trades
        if trend == 'uptrend':
            if curr_zone_bottom < current_close <= curr_zone_top:
                risk = current_close - curr_zone_bottom
                if risk <= 0:
                    print("✨ Calculated risk for LONG trade is non-positive. Skipping...")
                    return
                potential_reward = risk * self.eff_risk_reward
                take_profit = current_close + potential_reward

                if take_profit > current_close + (2 * recent_range):
                    print(f"✨ TP target ({take_profit:.2f}) too far from current price. LONG trade skipped!")
                    return

                risk_amount = self.equity * self.eff_risk_percent
                position_size = int(risk_amount / risk)
                stop_loss = curr_zone_bottom * 0.999

                print(f"✨ LONG signal detected! Entry = {current_close:.2f}, Stop Loss = {stop_loss:.2f}, Take Profit = {take_profit:.2f}, Size = {position_size}")
                self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                return

        # Entry logic for short trades
        elif trend == 'downtrend':
            if curr_zone_bottom <= current_close < curr_zone_top:
                risk = curr_zone_top - current_close
                if risk <= 0:
                    print("✨ Calculated risk for SHORT trade is non-positive. Skipping...")
                    return
                potential_reward = risk * self.eff_risk_reward
                take_profit = current_close - potential_reward

                if take_profit < current_close - (2 * recent_range):
                    print(f"✨ TP target ({take_profit:.2f}) too far from current price. SHORT trade skipped!")
                    return

                risk_amount = self.equity * self.eff_risk_percent
                position_size = int(risk_amount / risk)
                stop_loss = curr_zone_top * 1.001

                print(f"✨ SHORT signal detected! Entry = {current_close:.2f}, Stop Loss = {stop_loss:.2f}, Take Profit = {take_profit:.2f}, Size = {position_size}")
                self.sell(size=position_size, sl=stop_loss, tp=take_profit)
                return

        print("✨ No valid trade signal on this bar. Scanning for the perfect setup...")

if __name__ == "__main__":
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
    chart_dir = BASE_DIR / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)
    chart_file = chart_dir / f"{strategy_name}_chart.html"
    print(f"✨ Saving initial performance plot to {chart_file}")
    bt.plot(filename=str(chart_file), open_browser=False)

    # Parameter optimization
    print("✨ Starting parameter optimization...")
    optimized_stats = bt.optimize(
        eff_risk_reward=range(25, 31, 1),     # Effective risk_reward: 2.5:1 to 3.0:1
        eff_risk_percent=range(1, 3, 1),      # 1% to 2% risk per trade
        consolidation_span=range(2, 6),        # Consolidation span from 2 to 5 bars
        maximize='Equity Final [$]',
        return_heatmap=False
    )

    print("✨ Optimization complete!")
    print("✨ Optimized Stats:")
    print(optimized_stats)

    # Save optimized performance plot
    opt_chart_file = chart_dir / f"{strategy_name}_optimized_chart.html"
    print(f"✨ Saving optimized performance plot to {opt_chart_file}")
    bt.plot(filename=str(opt_chart_file), open_browser=False)

    print("✨ All done! Happy backtesting!")
