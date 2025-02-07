"""
Custom Strategy
Advanced trading strategy implementation
"""

from .base_strategy import BaseStrategy
import talib
import numpy as np

class CustomStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.name = "Custom Strategy"
        self.description = "Advanced trading strategy using multiple indicators"
        
    def calculate_signals(self, data):
        """Calculate trading signals based on multiple indicators"""
        close = data['close'].values
        high = data['high'].values
        low = data['low'].values
        
        # Calculate indicators
        sma = talib.SMA(close, timeperiod=20)
        rsi = talib.RSI(close, timeperiod=14)
        atr = talib.ATR(high, low, close, timeperiod=14)
        
        # Generate signals
        signals = np.zeros(len(close))
        signals[(close > sma) & (rsi < 30)] = 1  # Buy signal
        signals[(close < sma) & (rsi > 70)] = -1  # Sell signal
        
        return signals
