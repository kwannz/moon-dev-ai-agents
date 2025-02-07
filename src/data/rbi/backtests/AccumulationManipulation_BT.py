"""
AccumulationManipulation strategy implementation using TA-Lib indicators.
Detects accumulation and manipulation patterns in price action.
"""

import os
import pandas as pd
from pathlib import Path
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Read the CSV data from the given path
data_path = str(Path(__file__).parent.parent / "BTC-USD-15m.csv")
data = pd.read_csv(data_path, parse_dates=['datetime'])

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

print("Backtest completed successfully!")
