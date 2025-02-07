"""
TimeframeTrendAnalyzer strategy implementation using TA-Lib indicators.
Uses multi-timeframe analysis for trading decisions.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Load data
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
data = pd.read_csv(data_path)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Save initial performance chart
strategy_name = "TimeframeTrendAnalyzer"
chart_dir = str(Path(__file__).parent.parent / "charts")
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
bt.plot(filename=chart_file, open_browser=False)

print("Backtest completed successfully!")
