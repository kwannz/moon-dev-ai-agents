#!/usr/bin/env python3
"""
Lumix Backtest AI - TimeframeTrendDivergence Strategy
This script implements a backtest for the TimeframeTrendDivergence strategy,
which uses multi-timeframe analysis to identify potential trend divergences.

The strategy:
• Clean the data (remove spaces, drop unnamed columns, and remap column names)
• Resample the 15m data into Weekly, Daily, 4H, 1H and 50-minute bars.
• Check that the weekly and daily market structures are bullish.
• Determine a clear trend on the 4H timeframe (or fallback to 1H if 4H is unclear).
• Wait for a breakout on the 50-minute chart.
• Enter trades with proper risk management and position sizing.

Risk management and parameter optimization settings are built in.
Debug prints are included for easy tracing! ✨
"""

import os
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# *******************************************************************************
# STRATEGY DEFINITION
# *******************************************************************************

class TimeframeTrendDivergence(Strategy):
    # Internal variable to hold pending signal: None, 'pending_long', or 'pending_short'
    pending_signal = None

    def init(self):
        # Build aggregated series for multi-timeframe analysis.
        # Data is 15-minute candles. We now create weekly, daily, 4hour, 1hour resampled bars.
        print("✨ Initializing aggregated timeframes...")
        df = self.data.df.copy()  # full data; backtesting.py provides .df on self.data
        # Create weekly bars
        self.weekly = df.resample('W').agg({'Open':'first','High':'max','Low':'min','Close':'last'})
        self.weekly = self.weekly.reindex(df.index, method='ffill')
        # Create daily bars
        self.daily = df.resample('D').agg({'Open':'first','High':'max','Low':'min','Close':'last'})
        self.daily = self.daily.reindex(df.index, method='ffill')
        # Create 4-hour bars
        self.h4 = df.resample('4H').agg({'Open':'first','High':'max','Low':'min','Close':'last'})
        self.h4 = self.h4.reindex(df.index, method='ffill')
        # Create 1-hour bars
        self.h1 = df.resample('1H').agg({'Open':'first','High':'max','Low':'min','Close':'last'})
        self.h1 = self.h1.reindex(df.index, method='ffill')
        print("✨ Aggregated timeframes ready.")

        # Initialize technical indicators
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20)
