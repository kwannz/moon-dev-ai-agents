#!/usr/bin/env python3
"""
MACD Crossover Strategy ✨
- Uses MACD crossovers to identify potential trend changes
- Implements proper risk management with fixed risk per trade
- Includes debug messages and logging ✨
"""

import os
import pandas as pd
import numpy as np
import talib as ta
from backtesting import Backtest, Strategy

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "BTC-USD-15m.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "backtests/charts")

def load_and_clean_data():
    """Load and clean the OHLCV data"""
    print("✨ Loading the data...")
    
    # Load the data
    df = pd.read_csv(DATA_PATH)
    
    # Drop unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Ensure datetime index
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower()
    return df

class MACDCrossover(Strategy):
    # Strategy parameters (for optimization)
    fast_period = 12
    slow_period = 26
    signal_period = 9
    atr_period = 14
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        """Initialize the strategy with MACD and ATR indicators"""
        print("✨ Calculating indicators...")
        
        # Calculate MACD
        macd = self.I(ta.macd, self.data.Close, 
                     fast=self.fast_period, 
                     slow=self.slow_period,
                     signal=self.signal_period)
        self.macd_line = macd[0]
        self.signal_line = macd[1]
        self.macd_hist = macd[2]
        
        # Calculate ATR for position sizing
        self.atr = self.I(ta.ATR, self.data.High, self.data.Low, 
                         self.data.Close, timeperiod=self.atr_period)
    
    def next(self):
        """Execute trading logic for the current candle"""
        if len(self.data) < 2:  # Need at least 2 bars
            return
        
        # Calculate current values
        current_close = self.data.Close[-1]
        current_atr = self.atr[-1]
        
        # Calculate risk amount based on equity
        risk_amount = self.equity * self.risk_per_trade
        
        # LONG entry logic
        if self.macd_line[-2] < self.signal_line[-2] and self.macd_line[-1] > self.signal_line[-1]:
            # Calculate stop loss and take profit
            stop_loss = current_close - 2 * current_atr
            take_profit = current_close + 3 * current_atr  # 1.5:1 reward-to-risk
            
            # Calculate position size based on risk
            risk_per_unit = current_close - stop_loss
            pos_size = int(risk_amount / risk_per_unit) if risk_per_unit > 0 else 0
            
            if pos_size > 0 and not self.position:  # Check we're not already in a position
                print(f"✨ [LONG ENTRY] Spotted a Bullish MACD Signal! Entry: {current_close:.2f}")
                print(f"   ➡ Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}")
                print(f"   ➡ Position Size: {pos_size} units")
                print(f"   ➡ Risk Amount: ${risk_amount:.2f}, Risk per unit: ${risk_per_unit:.2f}")
                self.buy(size=pos_size, sl=stop_loss, tp=take_profit)
        
        # SHORT entry logic
        elif self.macd_line[-2] > self.signal_line[-2] and self.macd_line[-1] < self.signal_line[-1]:
            # Calculate stop loss and take profit
            stop_loss = current_close + 2 * current_atr
            take_profit = current_close - 3 * current_atr  # 1.5:1 reward-to-risk
            
            # Calculate position size based on risk
            risk_per_unit = stop_loss - current_close
            pos_size = int(risk_amount / risk_per_unit) if risk_per_unit > 0 else 0
            
            if pos_size > 0 and not self.position:  # Check we're not already in a position
                print(f"✨ [SHORT ENTRY] Spotted a Bearish MACD Signal! Entry: {current_close:.2f}")
                print(f"   ➡ Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}")
                print(f"   ➡ Position Size: {pos_size} units")
                print(f"   ➡ Risk Amount: ${risk_amount:.2f}, Risk per unit: ${risk_per_unit:.2f}")
                self.sell(size=pos_size, sl=stop_loss, tp=take_profit)

# Load and prepare data
data = load_and_clean_data()

# Initialize and run backtest
bt = Backtest(data, MACDCrossover, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n✨ Initial Backtest Stats:")
print(stats)

# Plot and save chart
chart_file = os.path.join(CHARTS_DIR, f"MACDCrossover_chart_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html")
bt.plot(filename=chart_file, open_browser=False)
print(f"✨ Chart saved to: {chart_file}")
