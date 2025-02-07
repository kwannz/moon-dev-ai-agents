"""
GapAndGoProfiter strategy implementation using TA-Lib indicators.
Includes data cleansing, position sizing, and parameter optimization.
Sets stop-loss based on recent low and take-profit target defined by risk-reward ratio.
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
import talib
from backtesting import Backtest, Strategy

# ------------------------------
# CUSTOM INDICATOR FUNCTIONS
# ------------------------------
def vwap_func(close, high, low, volume):
    # Calculate the Volume Weighted Average Price (VWAP)
    # Typical price = (High + Low + Close) / 3.0 then compute cumulative sums.
    typical_price = (high + low + close) / 3.0
    cum_vol = np.cumsum(volume)
    cum_pv = np.cumsum(typical_price * volume)
    return cum_pv / np.where(cum_vol == 0, 1, cum_vol)  # avoid divide by zero

# ------------------------------
# STRATEGY CLASS DEFINITION
# ------------------------------
class GapAndGoProfiter(Strategy):
    """
    GapAndGoProfiter Strategy 🌙🚀
    
    Parameters (to be optimized):
        gap_pct_perc   - Gap percentage in whole numbers compared to previous close (default=2 means 2%)
        risk_pct_perc  - Risk percentage per trade (default=1 means 1% of total equity)
        risk_reward    - Risk/reward ratio (default=2 means take profit = entry + 2 * risk)
     
    Operational logic:
      1. On a new candle, check if the open is at least gap_pct above the previous candle’s close.
      2. If true, then wait for a “pullback” candle that touches the 9-SMA or VWAP and then makes a new high.
      3. When found, calculate risk as (entry - candle low) and invest risk_pct of total equity.
      4. Set a stop loss at the candle low and a take profit based on risk_reward.
      5. Exit early if the price falls below the 9-SMA (a Moon Dev safety signal ✨).
    """
    # Optimization parameters: using whole-number percentages for easier optimization via range()
    gap_pct_perc = 2     # e.g., 2 -> 2% gap up
    risk_pct_perc = 1    # 1% risk per trade
    risk_reward   = 2    # take profit = entry + risk * 2

    def init(self):
        # Convert percentage parameters to decimals for calculation.
        self.gap_pct = self.gap_pct_perc / 100.0
        self.risk_pct = self.risk_pct_perc / 100.0
        
        # Compute indicators using the self.I() wrapper (always!)
        self.sma9  = self.I(talib.SMA, self.data.Close, timeperiod=9)
        self.vwap  = self.I(vwap_func, self.data.Close, self.data.High,
                                 self.data.Low, self.data.Volume)
        
        # Debug initialization print
        print("🌙✨ Initialized GapAndGoProfiter with parameters: gap_pct = {:.2%}, risk_pct = {:.2%}, risk_reward = {}".format(
            self.gap_pct, self.risk_pct, self.risk_reward))
    
    def next(self):
        # Avoid index errors by ensuring at least 2 bars
        if len(self.data) < 2:
            return
        
        # Current index: -1; previous index: -2
        current_open  = self.data.Open[-1]
        current_close = self.data.Close[-1]
        previous_close = self.data.Close[-2]
        current_low   = self.data.Low[-1]
        current_high  = self.data.High[-1]
        prev_high     = self.data.High[-2]
        
        # ------------------------------
        # ENTRY LOGIC
        # ------------------------------
        # Check for a gap up relative to the previous candle's close.
        if not self.position:
            if current_open >= previous_close * (1 + self.gap_pct):
                print("🌙🚀 Gap detected! Current Open ({}) is >= {} (%) gap above Previous Close ({}).".format(
                    current_open, self.gap_pct_perc, previous_close))
                # Now wait for a pullback candle touching SMA9 or VWAP AND making a new high
                if (current_low <= self.sma9[-1] * 1.001 or current_low <= self.vwap[-1] * 1.001) and (current_high > prev_high):
                    entry_price = current_close
                    stop_loss = current_low
                    risk = entry_price - stop_loss
                    if risk <= 0:
                        print("🌙❌ Risk calculation error: risk (entry-stop_loss) <= 0. Skipping entry.")
                        return

                    # Calculate risk amount based on total account equity. Our cash: 1,000,000.
                    risk_amount = self.equity * self.risk_pct
                    position_size = risk_amount / risk
                    # IMPORTANT: round position size to an integer (units)
                    position_size = int(round(position_size))
                    
                    if position_size <= 0:
                        print("🌙❌ Calculated position size is 0. Skipping entry.")
                        return
                    
                    # Calculate take profit level using the risk_reward ratio.
                    take_profit = entry_price + risk * self.risk_reward

                    print("🌙🚀 ENTRY SIGNAL: BUY {} units at price {} | Stop Loss: {} | Take Profit: {}".format(
                        position_size, entry_price, stop_loss, take_profit))
                    
                    # Place a buy order via backtesting.py's order function
                    self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                    
        # ------------------------------
        # EXIT LOGIC
        # ------------------------------
        # Also exit early if we are in a position and the price falls below the 9-SMA (safety signal).
        if self.position:
            if current_close < self.sma9[-1]:
                print("🌙✨ EXIT SIGNAL: Price ({}) dipped below SMA9 ({}). Exiting position.".format(
                    current_close, self.sma9[-1]))
                self.position.close()

# ------------------------------
# MAIN BACKTESTING EXECUTION
# ------------------------------
def run_backtest():
    # ------------------------------
    # DATA HANDLING
    # ------------------------------
    data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
    print("🌙 Reading data from: {}".format(data_path))
    data = pd.read_csv(data_path)
    
    # Clean column names: strip spaces and lower-case, then drop unnamed columns.
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    
    # Map columns to required names with proper case.
    cols_map = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'datetime': 'DateTime'}
    data.rename(columns=cols_map, inplace=True)
    
    # Optionally convert DateTime column to datetime type if exists
    if 'DateTime' in data.columns:
        data['DateTime'] = pd.to_datetime(data['DateTime'])
    
    print("🌙 Data columns after cleaning: ", list(data.columns))
    
    # ------------------------------
    # INITIAL BACKTEST
    # ------------------------------
    initial_cash = 1000000  # size should be 1,000,000
    bt = Backtest(data, GapAndGoProfiter, cash=initial_cash, commission=0.0, exclusive_orders=True)
    
    print("🌙🚀 Running initial backtest with default parameters...")
    stats = bt.run()
    print("🌙 Full Stats:\n", stats)
    print("🌙 Strategy details:\n", stats._strategy)
    
    # Save initial chart to charts directory
    strategy_name = "GapAndGoProfiter"
    chart_file = os.path.join(str(Path(__file__).parent.parent / "charts"),
                              f"{strategy_name}_initial_chart.html")
    print("🌙 Saving initial performance chart to: {}".format(chart_file))
    bt.plot(filename=chart_file, open_browser=False)
    
    # ------------------------------
    # PARAMETER OPTIMIZATION
    # ------------------------------
    print("🌙🚀 Starting parameter optimization...")
    optimized_stats = bt.optimize(
        gap_pct_perc=range(1, 5, 1),      # try gap percentages 1% to 4%
        risk_pct_perc=range(1, 3, 1),       # try risk between 1% and 2%
        risk_reward=range(1, 4, 1),         # try risk/reward ratios: 1,2,3
        maximize='Equity Final [$]',
        constraint=lambda param: True,     # No extra constraints
        return_stats=True
    )
    
    print("🌙 Optimized Result:\n", optimized_stats)
    
    # Save optimized chart to charts directory (using best parameters)
    chart_file_opt = os.path.join(str(Path(__file__).parent.parent / "charts"),
                                  f"{strategy_name}_optimized_chart.html")
    print("🌙 Saving optimized performance chart to: {}".format(chart_file_opt))
    bt.plot(filename=chart_file_opt, open_browser=False)

if __name__ == '__main__':
    run_backtest()

print("Backtest completed successfully!")
"""
Implementation Notes:
- Uses standard imports (os, pandas, numpy, talib, backtesting)
- Cleans data columns (spaces removed, lowercased)
- Computes indicators using self.I() wrapper with TA-Lib
- Entry on gap up >= gap_pct with pullback to SMA9/VWAP
- Stop loss at candle low, take profit based on risk-reward ratio
- Position size calculated using risk amount and risk per unit
- Saves initial and optimized performance charts
"""

print("Backtest completed successfully!")
