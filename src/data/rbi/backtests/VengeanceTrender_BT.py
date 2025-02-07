"""
VengeanceTrender strategy implementation using TA-Lib indicators.
Uses trend following with ATR-based trailing stops.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

def prepare_data(data_path):
    data = pd.read_csv(data_path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    return data

# Load and prepare data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
data = prepare_data(data_path)

# Initialize and run backtest
bt = Backtest(data, VengeanceTrender, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)

# Save initial plot
chart_file = os.path.join(str(Path(__file__).parent.parent / "charts"), "VengeanceTrender_initial_chart.html")
bt.plot(filename=chart_file, open_browser=False)

print("Backtest completed successfully!")
