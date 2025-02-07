#!/usr/bin/env python3
"""
Lumix Backtest AI - TimeframeTrendAnalyzer Strategy
This script implements a backtest for the TimeframeTrendAnalyzer strategy,
which uses multi-timeframe market structure analysis and price‐action breakout
to identify potential entry points. The strategy works as follows:

• Clean the data (remove spaces, drop unnamed columns, and remap column names)
• Resample the 15m data into Weekly, Daily, 4H, 1H and 50-minute bars.
• Check that the weekly and daily market structures are bullish.
• Determine a clear trend on the 4H timeframe (or fallback to 1H if 4H is unclear).
• Wait for a breakout on the 50-minute chart:
    – For a bullish trend: a 50-min close above the previous 50-min high.
    – For a bearish trend: a 50-min close below the previous 50-min low.
• When a breakout is confirmed, calculate risk using the previous 50-min bar’s low/high
  and enter a trade with stop loss and take profit (aiming for a risk–reward ratio).
• The position size is calculated with proper integer rounding.

Risk management and parameter optimization settings are built in.
Debug prints are included for easy tracing! ✨
"""

import os
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# ============================================================================
# STRATEGY CLASS
# ============================================================================

class TimeframeTrendAnalyzer(Strategy):
    # Optimization parameters:
    # risk_pct_percent: risk per trade in percentage points (e.g., 1 means 1%)
    # risk_reward: risk-reward ratio (target multiples of risk)
    risk_pct_percent = 1      # Default: 1% risk per trade
    risk_reward = 2.0         # Default risk-reward ratio

    def init(self):
        print("✨ [INIT] Initializing TimeframeTrendAnalyzer strategy...")
        # Resample the original 15-minute OHLCV data into higher timeframes.
        # Using backtesting.py's self.data (a pandas DataFrame) for indicator calculations.
        self.weekly_data = self.data.resample('W', closed='right', label='right').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        self.daily_data = self.data.resample('D', closed='right', label='right').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        self.fourhour_data = self.data.resample('4H', closed='right', label='right').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        self.onehour_data = self.data.resample('1H', closed='right', label='right').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        self.fiftymin_data = self.data.resample('50T', closed='right', label='right').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        print("✨ [INIT] Aggregated weekly, daily, 4H, 1H, and 50min data computed!")

    def get_last_bar(self, df, current_time):
        "Helper: return the last bar in df with timestamp <= current_time."
        try:
            subset = df.loc[:current_time]
            if subset.empty:
                return None
            return subset.iloc[-1]
        except IndexError:
            return df.iloc[-1]
