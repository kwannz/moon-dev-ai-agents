"""
StochasticPhaseTrader strategy implementation using TA-Lib indicators.
Uses stochastic oscillator phases for trading decisions.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

def stochrsi_func(close, period, fastk_period, fastd_period):
    rsi = talib.RSI(close, timeperiod=period)
    min_rsi = talib.MIN(rsi, timeperiod=period)
    max_rsi = talib.MAX(rsi, timeperiod=period)
    stoch_rsi = 100 * ((rsi - min_rsi) / (max_rsi - min_rsi + 1e-10))
    fastk = talib.SMA(stoch_rsi, timeperiod=fastk_period)
    fastd = talib.SMA(fastk, timeperiod=fastd_period)
    return fastk, fastd

class StochasticPhaseTrader(Strategy):
    period = 14
    fastk_period = 3
    fastd_period = 3
    oversold = 20
    overbought = 80
    risk_percent = 0.01
    sl_pct = 0.02

    def init(self):
        self.stochk, self.stochd = self.I(stochrsi_func, self.data.Close,
                                         self.period, self.fastk_period, self.fastd_period)
        self.last_buy_stoch = None
        print("StochasticPhaseTrader initialized with parameters:")
        print(f"      period={self.period}, fastk_period={self.fastk_period}, fastd_period={self.fastd_period}")
        print(f"      oversold threshold={self.oversold}, overbought threshold={self.overbought}")
        print(f"      risk_percent={self.risk_percent}, sl_pct={self.sl_pct}")
    
    def next(self):
        current_close = self.data.Close[-1]
        current_k = self.stochk[-1]
        prev_k = self.stochk[-2] if len(self.stochk) > 1 else current_k
        print(f"Candle @ {self.data.index[-1]} | Close: {current_close:.2f} | StochK: {current_k:.2f}")

        if not self.position:
            if prev_k > self.oversold and current_k <= self.oversold:
                entry_price = current_close
                stop_loss = entry_price * (1 - self.sl_pct)
                risk_amount = self.equity * self.risk_percent
                risk_per_unit = entry_price - stop_loss
                position_size = risk_amount / risk_per_unit
                position_size = int(round(position_size))
                if position_size < 1:
                    position_size = 1
                print(f"BUY signal generated!")
                print(f"      Entry Price: {entry_price:.2f}, Stop Loss: {stop_loss:.2f}, Position Size: {position_size}")
                self.buy(size=position_size, sl=stop_loss)
                self.last_buy_stoch = current_k

        else:
            if self.last_buy_stoch is not None and current_k < self.last_buy_stoch:
                entry_price = current_close
                stop_loss = entry_price * (1 - self.sl_pct)
                risk_amount = self.equity * self.risk_percent
                risk_per_unit = entry_price - stop_loss
                add_size = risk_amount / risk_per_unit
                add_size = int(round(add_size))
                if add_size < 1:
                    add_size = 1
                print(f"Additional BUY signal (DCA) at {entry_price:.2f} with size {add_size}")
                self.buy(size=add_size, sl=stop_loss)
                self.last_buy_stoch = current_k

            if prev_k < self.overbought and current_k >= self.overbought:
                print("SELL signal generated! StochK crossed above the overbought threshold.")
                self.position.close()
                self.last_buy_stoch = None

if __name__ == '__main__':
    data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
    print("Loading data from:", data_path)
    data = pd.read_csv(data_path, parse_dates=['datetime'])
    
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data.rename(columns={'open': 'Open', 
                        'high': 'High', 
                        'low': 'Low', 
                        'close': 'Close', 
                        'volume': 'Volume',
                        'datetime': 'Date'}, inplace=True)
    data.set_index('Date', inplace=True)
    print("Data cleaning complete. Columns:", data.columns.tolist())

    bt = Backtest(data, StochasticPhaseTrader, cash=1000000, commission=.000,
                 exclusive_orders=True)

    print("Running initial backtest with default parameters...")
    stats = bt.run()
    print("Full Stats:")
    print(stats)
    print("Strategy details:")
    print(stats._strategy)

    charts_dir = str(Path(__file__).parent.parent / "charts")
    os.makedirs(charts_dir, exist_ok=True)
    strategy_name = "StochasticPhaseTrader"
    chart_file_initial = os.path.join(charts_dir, f"{strategy_name}_chart_initial.html")
    print(f"Saving initial performance plot to: {chart_file_initial}")
    bt.plot(filename=chart_file_initial, open_browser=False)

    print("Running parameter optimization...")
    optimized_stats = bt.optimize(
        oversold=range(15, 25, 5),
        overbought=range(75, 85, 5),
        sl_pct=[0.01, 0.02, 0.03],
        maximize='Equity Final [$]',
        constraint=lambda param: param.oversold < param.overbought
    )
    print("Optimized Stats:")
    print(optimized_stats)

    chart_file_optimized = os.path.join(charts_dir, f"{strategy_name}_chart_optimized.html")
    print(f"Saving optimized performance plot to: {chart_file_optimized}")
    bt.plot(filename=chart_file_optimized, open_browser=False)

print("Backtest completed successfully!")
