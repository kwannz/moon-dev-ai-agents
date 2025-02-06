TRADING_CONFIG = {
    "pairs": ["BTC/USD", "ETH/USD"],  # Trading pairs
    "interval": "1m",                  # Trading interval
    "risk_percentage": 1.0,            # Max risk per trade
    "stop_loss": 2.0,                  # Stop loss percentage
    "take_profit": 3.0                 # Take profit percentage
}

# Market configuration
MAX_POSITION_PERCENTAGE = 20  # Maximum percentage of portfolio per position
CASH_PERCENTAGE = 20         # Minimum cash buffer percentage
SLEEP_BETWEEN_RUNS_MINUTES = 15  # Time between trading cycles
