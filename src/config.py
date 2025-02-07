"""
Lumix Trading System Configuration
"""

# Token Addresses
USDC_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC token address
SOL_ADDRESS = "So11111111111111111111111111111112"   # Native SOL token address

# Trading Exclusions
EXCLUDED_TOKENS = [USDC_ADDRESS, SOL_ADDRESS]  # Never trade these tokens

# Token List for Trading
MONITORED_TOKENS = [
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump',  # FART
    'HeLp6NuQkmYB4pYWo2zYs22mESHXPQYzXbB8n4V98jwC'   # AI16Z
]

# Trading List Configuration
tokens_to_trade = MONITORED_TOKENS

# Wallet Configuration
WALLET_ADDRESS = "4BKPzFyjBaRP3L1PNDf3xTerJmbbxxESmDmZJ2CZYdQ5"  # Trading wallet address
DEFAULT_SYMBOL = '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'

# Position Sizing and Trading Parameters
POSITION_SIZE_SOL = 0.05  # Maximum position size in SOL
MAX_ORDER_SIZE_SOL = 0.02  # Maximum order size in SOL
TX_SLEEP = 15  # Sleep between transactions (seconds)
SLIPPAGE = 250  # 250 = 2.5% slippage for optimal execution
PRIORITY_FEE = 100000  # ~0.02 USD at current SOL prices
ORDERS_PER_OPEN = 2  # Multiple orders for better fill rates
MAX_RETRIES = 3  # Maximum retry attempts for failed transactions

# Risk Management Settings
MIN_SOL_BALANCE = 0.05  # Minimum SOL balance required for trading
CASH_PERCENTAGE = 30  # Minimum % to keep in SOL as safety buffer
MAX_POSITION_PERCENTAGE = 20  # Maximum % allocation per position
MAX_LOSS_PERCENTAGE = 5  # Maximum loss percentage per trade
MAX_DAILY_TRADES = 10  # Maximum number of trades per day
SLEEP_AFTER_CLOSE = 300  # Prevent overtrading (5 minutes)

# Trading Monitoring
MAX_LOSS_GAIN_CHECK_HOURS = 12  # How far back to check for max loss/gain limits
SLEEP_BETWEEN_RUNS_MINUTES = 15  # Sleep between agent runs


# Max Loss/Gain Settings FOR RISK AGENT 1/5/25
USE_PERCENTAGE = False  # If True, use percentage-based limits. If False, use USD-based limits

# USD-based limits (used if USE_PERCENTAGE is False)
MAX_LOSS_USD = 25  # Maximum loss in USD before stopping trading
MAX_GAIN_USD = 25 # Maximum gain in USD before stopping trading

# USD MINIMUM BALANCE RISK CONTROL
MINIMUM_BALANCE_USD = 50  # If balance falls below this, risk agent will consider closing all positions
USE_AI_CONFIRMATION = True  # If True, consult AI before closing positions. If False, close immediately on breach

# Percentage-based limits (used if USE_PERCENTAGE is True)
MAX_LOSS_PERCENT = 5  # Maximum loss as percentage (e.g., 20 = 20% loss)
MAX_GAIN_PERCENT = 5  # Maximum gain as percentage (e.g., 50 = 50% gain)

# Transaction Settings
SLIPPAGE = 250  # 250 = 2.5% slippage for optimal trade execution
PRIORITY_FEE = 100000  # ~0.02 USD at current SOL prices
ORDERS_PER_OPEN = 2  # Multiple orders for better fill rates
MAX_RETRIES = 3  # Maximum retry attempts for failed transactions
MIN_AMOUNT_OUT_BPS = 9700  # 97% of quote amount for minAmountOut protection

# Market maker settings 📊
buy_under = .0946
sell_over = 1

# Market Data Configuration
TIMEFRAME = '15m'  # Trading timeframe
LOOKBACK_DAYS = 3  # Days of historical data to analyze
MIN_VOLUME_24H = 1000  # Minimum 24h volume in USD
MIN_LIQUIDITY = 5000  # Minimum liquidity in USD
SAVE_MARKET_DATA = False  # Only use temp data during run

# AI Model Settings 🤖
AI_MODEL = "claude-3-haiku-20240307"  # Model Options:
                                     # - claude-3-haiku-20240307 (Fast, efficient Claude model)
                                     # - claude-3-sonnet-20240229 (Balanced Claude model)
                                     # - claude-3-opus-20240229 (Most powerful Claude model)
AI_MAX_TOKENS = 1024  # Max tokens for response
AI_TEMPERATURE = 0.7  # Creativity vs precision (0-1)

# Trading Strategy Agent Settings - MAY NOT BE USED YET 1/5/25
ENABLE_STRATEGIES = True  # Set this to True to use strategies
STRATEGY_MIN_CONFIDENCE = 0.7  # Minimum confidence to act on strategy signals

# Sleep time between main agent runs
SLEEP_BETWEEN_RUNS_MINUTES = 15  # How long to sleep between agent runs 🕒

# Future variables (not active yet) 🔮
sell_at_multiple = 3
USDC_SIZE = 1
limit = 49
timeframe = '15m'
stop_loss_perctentage = -.24
EXIT_ALL_POSITIONS = False
DO_NOT_TRADE_LIST = ['777']
CLOSED_POSITIONS_TXT = '777'
minimum_trades_in_last_hour = 777
