"""
TimeframeTrendDivergence strategy implementation.
Pre-aggregates 15-minute data into multiple timeframes and uses TA-Lib indicators.
"""

#!/usr/bin/env python3
import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Data preparation
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
print("✨ Loading data from:", data_path)
df = pd.read_csv(data_path)

# Clean up column names
df.columns = df.columns.str.strip().str.lower()
# Drop any unnamed columns
df = df.drop(columns=[col for col in df.columns if 'unnamed' in col.lower()])

# Rename columns to proper case required by backtesting.py: Open, High, Low, Close, Volume
df.rename(columns={'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'}, inplace=True)

# Convert datetime column and set as index (if exists)
if 'datetime' in df.columns:
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

print("✨ Data loaded and cleaned! Total rows:", len(df))
  
# *******************************************************************************
# STRATEGY DEFINITION
# *******************************************************************************
class TimeframeTrendDivergence(Strategy):
    # Optimization parameters with default values
    risk_pct = 0.01                 # 1% risk per trade
    risk_reward_ratio = 2.0         # Risk to reward ratio (can be optimized to 2 or 3)
    conso_factor = 1.0              # 4-hour consolidation factor multiplier
    
    # Internal variable to hold pending signal: None, 'pending_long', or 'pending_short'
    pending_signal = None

    def init(self):
        # Build aggregated series for multi-timeframe analysis.
        # Data is 15-minute candles. We now create weekly, daily, 4hour, 1hour resampled bars.
        print("✨ Initializing aggregated timeframes…")
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

        # (Any TA-lib indicator using self.I must be wrapped here, even if not strictly needed.)
        # For illustration, suppose we wanted to compute a SMA on the 15-minute close.
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20)

    def next(self):
        # Get current bar index (an integer counter)
        i = self.bar
        
        # Get current aggregated bars using self.bar as the index position
        weekly_bar = self.weekly.iloc[i]
        daily_bar  = self.daily.iloc[i]
        h4_bar     = self.h4.iloc[i]
        h1_bar     = self.h1.iloc[i]
        current_price = self.data.Close[i]
        time_now = self.data.index[i]
        
        # Debug prints
        print(f"✨ [{time_now}] Bar {i}: Price = {current_price:.2f}")

        # CONDITION CHECK: Only look for new signals if not already in a trade and no pending signal.
        if not self.position and self.pending_signal is None:
            # Check if the weekly and daily sessions are bullish
            bullish_weekly = weekly_bar['Close'] > weekly_bar['Open']
            bullish_daily  = daily_bar['Close']  > daily_bar['Open']
            if bullish_weekly and bullish_daily:
                print("✨ Weekly & Daily are bullish! (🌞)")
                
                # Check for 4-hour consolidation: we define consolidation as 4H range being less
                # than (conso_factor * median range over the last 10 4H bars)
                # Calculate current 4H range
                current_range = h4_bar['High'] - h4_bar['Low']
                # Get last 10 available 4H bars including current one; if not available, take what you have
                recent_ranges = self.h4.iloc[max(0, i-9):i+1]
                median_range = recent_ranges.apply(lambda row: row['High'] - row['Low'], axis=1).median()
                consolidation = current_range < (self.conso_factor * median_range)
                print(f"✨ 4H consolidation check: current_range = {current_range:.2f}, median_range = {median_range:.2f}, consolidation = {consolidation}")

                # Check the 1-hour trend direction (clear trend; not consolidation)
                bullish_h1 = h1_bar['Close'] > h1_bar['Open']
                bearish_h1 = h1_bar['Close'] < h1_bar['Open']
                if consolidation and (bullish_h1 or bearish_h1):
                    # Set pending signal based on 1-hour trend
                    self.pending_signal = 'pending_long' if bullish_h1 else 'pending_short'
                    direction = "LONG" if bullish_h1 else "SHORT"
                    print(f"✨ 1H indicates a {direction} trend. Setting pending signal: {self.pending_signal} (👀)")
        
        # If we have a pending signal, check for breakout in the 15-minute price
        if self.pending_signal is not None and not self.position:
            # For long: wait until price breaks above the current 1H high
            # For short: wait until price breaks below the current 1H low
            if self.pending_signal == 'pending_long' and current_price > h1_bar['High']:
                print(f"✨ LONG entry trigger! Price broke above 1H High {h1_bar['High']:.2f} 🚀")
                self.enter_trade('long', current_price, h1_bar)
                self.pending_signal = None  # reset signal after entry
            elif self.pending_signal == 'pending_short' and current_price < h1_bar['Low']:
                print(f"✨ SHORT entry trigger! Price broke below 1H Low {h1_bar['Low']:.2f} 🚀")
                self.enter_trade('short', current_price, h1_bar)
                self.pending_signal = None  # reset signal after entry
            # If the pending signal conditions are no longer met, you might cancel the signal.
            # (This example retains the pending signal until the breakout occurs.)
        
        # Optional: You can add additional debug prints on position updates.
        if self.position:
            print(f"✨ In trade: {self.position} with entry price {self.position.entry_price:.2f}")
    
    def enter_trade(self, trade_dir, entry_price, h1_bar):
        """
        Helper to enter a trade with risk management.
        For a LONG trade, stop loss is set at the 1H low.
        For a SHORT trade, stop loss is set at the 1H high.
        Take profit is determined based on the risk-reward ratio.
        Position sizing is based on a fixed risk percentage of equity.
        """
        equity = self.equity
        risk_amount = equity * self.risk_pct
        
        if trade_dir == 'long':
            stop_loss = h1_bar['Low']
            risk_per_unit = entry_price - stop_loss
            # Avoid division by zero.
            if risk_per_unit <= 0:
                print("✨ Risk per unit <= 0. Trade skipped. 😱")
                return
            take_profit = entry_price + risk_per_unit * self.risk_reward_ratio
            direction_text = "LONG"
        else:
            stop_loss = h1_bar['High']
            risk_per_unit = stop_loss - entry_price
            if risk_per_unit <= 0:
                print("✨ Risk per unit <= 0. Trade skipped. 😱")
                return
            take_profit = entry_price - risk_per_unit * self.risk_reward_ratio
            direction_text = "SHORT"
        
        # Calculate the recommended position size; ensure it is an integer number of units.
        position_size = risk_amount / risk_per_unit
        position_size = int(round(position_size))
        
        print(f"✨ Entering {direction_text} trade at {entry_price:.2f} with stop loss {stop_loss:.2f} and take profit {take_profit:.2f}.")
        print(f"✨ Equity = {equity:.2f}, Risk amount = {risk_amount:.2f}, Risk per unit = {risk_per_unit:.2f}, Calculated size = {position_size} units.")
        
        # Enter trade using backtesting.py's order method.
        if trade_dir == 'long':
            # For long trade, the buy order is placed.
            self.buy(size=position_size, sl=stop_loss, tp=take_profit)
        else:
            # For short trade, the sell order is placed (backtesting.py uses sell to short).
            self.sell(size=position_size, sl=stop_loss, tp=take_profit)
        
        # Debug message after entering
        print(f"✨ {direction_text} trade executed! 🚀")

# *******************************************************************************
# RUN INITIAL BACKTEST & OPTIMIZATION
# *******************************************************************************
if __name__ == '__main__':
    # Set initial cash to 1,000,000 as required
    initial_cash = 1000000

    # Create backtest object
    bt = Backtest(df, TimeframeTrendDivergence, cash=initial_cash, commission=.002,
                  exclusive_orders=True)

    print("✨ Running initial backtest...")
    stats = bt.run()
    print("\n✨ Initial Backtest Results:")
    print(stats)
    print("\n✨ Strategy details:")
    print(stats._strategy)

    # Save initial performance plot to chart directory
    strategy_name = "TimeframeTrendDivergence_initial"
    chart_dir = str(Path(__file__).parent.parent / "charts")
    chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
    print(f"Saving initial chart to: {chart_file}")
    bt.plot(filename=chart_file, open_browser=False)

    # *************************************************************************************
    # Optimization: vary risk_pct, risk_reward_ratio, and 4H consolidation factor parameters.
    # Note: Ranges are defined per requirements; always break down list parameters.
    # *************************************************************************************
    print("\n✨ Running optimization…")
    optimized_stats = bt.optimize(risk_pct=round, risk_reward_ratio=round, conso_factor=round,
                                  # Ranges for optimization:
                                  risk_pct = (0.005, 0.02, 0.005),              # 0.005 to 0.02 with step 0.005
                                  risk_reward_ratio = (2, 3, 1),                  # 2 or 3
                                  conso_factor = (0.8, 1.2, 0.2),                 # 0.8, 1.0, 1.2
                                  maximize='Equity Final [$]')
    
    print("\n✨ Optimized Backtest Results:")
    print(optimized_stats)
    print("\n✨ Optimized Strategy parameters:")
    print(optimized_stats._strategy)

    # Save optimized performance plot to chart directory
    strategy_name = "TimeframeTrendDivergence_optimized"
    chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
    print(f"✨ Saving optimized chart to: {chart_file}")
    bt.plot(filename=chart_file, open_browser=False)

    print("✨ Backtesting and optimization complete!")
    
"""
Strategy Notes:
- Uses self.I() to wrap TA-Lib calls for indicator calculations
- Aggregates bars (weekly, daily, 4H, 1H) via pandas resample
- Entry orders execute on 15-minute price breaks of 1-hour range
- Position size calculated using risk-based sizing
- Saves stats and plots to charts directory after initial backtest
"""
