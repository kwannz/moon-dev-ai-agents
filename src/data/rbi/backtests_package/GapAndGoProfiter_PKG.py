#!/usr/bin/env python3
"""
Lumix Backtest AI - Backtesting "GapAndGoProfiter"
This strategy looks for a significant gap-up from the previous day's close and,
after a pullback toward the 9-period moving average or VWAP, goes long. 
It sets a stop-loss based on the recent low and a take-profit target defined by a risk-reward ratio.
Debug prints are included for easy tracing! ✨
"""

import os
import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy

def vwap_func(df):
    """Calculate VWAP for a DataFrame with OHLCV data."""
    v = df['Volume'].values
    h = df['High'].values
    l = df['Low'].values
    c = df['Close'].values
    
    typical_price = (h + l + c) / 3
    return np.cumsum(v * typical_price) / np.cumsum(v)

class GapAndGoProfiter(Strategy):
    """
    GapAndGoProfiter Strategy
    
    This strategy:
      1. On a new candle, check if the open is at least gap_pct above the previous candle's close.
      2. If true, then wait for a "pullback" candle that touches the 9-SMA or VWAP and then makes a new high.
      3. When found, calculate risk as (entry - candle low) and invest risk_pct of total equity.
      4. Set a stop loss at the candle low and a take profit based on risk_reward.
      5. Exit early if the price falls below the 9-SMA (a safety signal ✨).
    """
    # Optimization parameters: using whole-number percentages for easier optimization via range()
    gap_pct_perc = 2     # e.g., 2 -> 2% gap up
    risk_pct_perc = 1    # 1% risk per trade
    risk_reward = 25     # 25 -> 2.5:1 reward-to-risk ratio
    
    def init(self):
        """Initialize strategy indicators."""
        # Convert percentage parameters to decimals
        self.gap_pct = self.gap_pct_perc / 100.0
        self.risk_pct = self.risk_pct_perc / 100.0
        self.rr_ratio = self.risk_reward / 10.0
        
        # Calculate 9-period SMA and VWAP
        self.sma9 = self.I(talib.SMA, self.data.Close, timeperiod=9)
        self.vwap = self.I(vwap_func, self.data)
        print("✨ Strategy initialized with gap threshold:", self.gap_pct)
        
    def next(self):
        """Execute trading logic for the current candle."""
        if len(self.data) < 2:  # Need at least 2 bars
            return
