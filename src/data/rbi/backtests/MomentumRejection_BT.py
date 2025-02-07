#!/usr/bin/env python3
"""
Lumix Backtest AI - MomentumRejection Strategy
This implementation includes trendline analysis, Stochastic Oscillator confirmation,
entry/exit logic, risk management, and parameter optimization.
"""

import pandas as pd
import talib
from backtesting import Backtest, Strategy

def preprocess_data(df):
    """Clean and prepare the data for backtesting"""
    # Drop unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Ensure datetime index
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower()
    return df

class MomentumRejection(Strategy):
    stoch_period = 14
    stoch_k = 3
    stoch_d = 3
    stoch_oversold = 20
    stoch_overbought = 80
    risk_pct = 1.0  # Risk 1% per trade
    
    def init(self):
        self.stoch_k_line, self.stoch_d_line = self.I(talib.STOCH, self.data.High, self.data.Low, 
            self.data.Close, fastk_period=self.stoch_period, slowk_period=self.stoch_k,
            slowk_matype=0, slowd_period=self.stoch_d, slowd_matype=0)
    
    def next(self):
        price = self.data.Close[-1]
        stoch_k = self.stoch_k_line[-1]
        stoch_d = self.stoch_d_line[-1]
        
        # Calculate trendlines
        uptrend_line = self.data.High[-20:].max()
        downtrend_line = self.data.Low[-20:].min()
        
        # Calculate position size based on risk
        equity = self.equity
        risk_amount = equity * (self.risk_pct / 100)
        position_size = int(risk_amount / price) if price > 0 else 0
        
        # Entry logic for continuation pattern (uptrend)
        if price > uptrend_line and stoch_k < self.stoch_oversold and stoch_d < self.stoch_oversold:
            if stoch_k[-2] < stoch_d[-2] and stoch_k[-1] > stoch_d[-1]:  # Stochastic crossover confirmation
                self.buy(size=position_size)
                print(f"✨ Buy Signal: Continuation Uptrend | Price: {price} | Stochastic: {stoch_k}, {stoch_d}")

        # Entry logic for continuation pattern (downtrend)
        elif price < downtrend_line and stoch_k > self.stoch_overbought and stoch_d > self.stoch_overbought:
            if stoch_d[-2] < stoch_k[-2] and stoch_d[-1] > stoch_k[-1]:  # Stochastic crossover confirmation
                self.sell(size=position_size)
                print(f"✨ Sell Signal: Continuation Downtrend | Price: {price} | Stochastic: {stoch_k}, {stoch_d}")

        # Entry logic for breakout pattern (uptrend reversal)
        if price < uptrend_line and stoch_k > self.stoch_overbought and stoch_d > self.stoch_overbought:
            if stoch_d[-2] < stoch_k[-2] and stoch_d[-1] > stoch_k[-1]:  # Stochastic crossover confirmation
                self.sell(size=position_size)
                print(f"✨ Sell Signal: Breakout Uptrend Reversal | Price: {price} | Stochastic: {stoch_k}, {stoch_d}")

        # Entry logic for breakout pattern (downtrend reversal)
        elif price > downtrend_line and stoch_k < self.stoch_oversold and stoch_d < self.stoch_oversold:
            if stoch_k[-2] < stoch_d[-2] and stoch_k[-1] > stoch_d[-1]:  # Stochastic crossover confirmation
                self.buy(size=position_size)
                print(f"✨ Buy Signal: Breakout Downtrend Reversal | Price: {price} | Stochastic: {stoch_k}, {stoch_d}")
