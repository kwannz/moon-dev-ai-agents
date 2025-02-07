"""
Example Strategy
Simple Moving Average Crossover Strategy Example
A basic strategy implementation using TA-Lib indicators
"""

from .base_strategy import BaseStrategy
import talib
import numpy as np

class ExampleStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.name = "Example Strategy"
        self.description = "Simple Moving Average Crossover Strategy"
        
    def calculate_signals(self, data):
        """Calculate trading signals based on SMA crossover"""
        close = data['close'].values
        
        # Calculate SMAs
        sma_fast = talib.SMA(close, timeperiod=20)
        sma_slow = talib.SMA(close, timeperiod=50)
        
        # Generate signals
        signals = np.zeros(len(close))
        signals[sma_fast > sma_slow] = 1  # Buy signal
        signals[sma_fast < sma_slow] = -1  # Sell signal
        
        return signals
