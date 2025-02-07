# Market Data API Documentation

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Authentication](#authentication)
- [Market Data Methods](#market-data-methods)
- [CopyBot Methods](#copybot-methods)
- [Utility Methods](#utility-methods)
- [Example Usage](#example-usage)

## Overview

The Lumix Market Data API (`src/agents/api.py`) provides access to real-time market data. The API is designed to be easy to use while providing powerful features for market analysis and automated trading.

## Installation

1. Ensure you have the required dependencies:
```bash
pip install requests pandas python-dotenv termcolor
```

2. Set up your environment variables:
```bash
# Create a .env file and add your Lumix API key
MOONDEV_API_KEY=your_api_key_here
```

## Authentication

The API uses an API key for authentication. This key should be stored in your `.env` file and will be automatically loaded when initializing the API client.

```python
from src.agents.api import MoonDevAPI

# Initialize the API client
api = MoonDevAPI()  # Automatically loads API key from .env
```

## Market Data Methods

### Get Liquidation Data
```python
# Get all liquidations
liq_data = api.get_liq_data()

# Get liquidations for specific symbol
btc_liq_data = api.get_liq_data(symbol="BTC", limit=100000)
```

### Get Funding Rate Data
```python
# Get all funding rates
funding_data = api.get_funding_rate()

# Get funding rate for specific symbol
btc_funding = api.get_funding_rate(symbol="BTC")
```

### Get Open Interest Data
```python
# Get symbol-specific open interest
oi_data = api.get_open_interest(symbol="BTC")

# Get total market open interest
total_oi = api.get_open_interest(total=True)
```

### Get New Token Launches
```python
# Get latest token launches
new_tokens = api.get_new_token_addresses()
```

## CopyBot Methods

### Get Follow List
```python
# Get current copy trading follow list
follow_list = api.get_copybot_follow_list()
```

### Get Recent Transactions
```python
# Get recent copy trading transactions
recent_txs = api.get_recent_transactions()
```

## Utility Methods

### List Available Files
```python
# Get list of all available data files
available_files = api.list_available_files()
```

## Example Usage

Here's a complete example showing how to use the API:

```python
from src.agents.api import MoonDevAPI
import time

# Initialize API
api = MoonDevAPI()

# Get BTC data
symbol = "BTC"

# Market Data
liq_data = api.get_liq_data(symbol)
funding_data = api.get_funding_rate(symbol)
oi_data = api.get_open_interest(symbol)

# CopyBot Data
follow_list = api.get_copybot_follow_list()
recent_txs = api.get_recent_transactions()

# List available files
api.list_available_files()
```

## Data Storage

By default, all data is saved to `src/agents/api_data/`. The following files are created:
- `liq_data.csv`: Liquidation data
- `funding.csv`: Funding rate data
- `oi.csv`: Open interest data
- `oi_total.csv`: Total market open interest
- `follow_list.csv`: Copy trading follow list
- `recent_txs.csv`: Recent copy trading transactions

## Error Handling

The API includes built-in error handling and will:
- Print colored error messages for easy debugging
- Return `None` if an API call fails
- Create data directories automatically
- Validate API responses

## 🚨 Important Notes

1. Never share or commit your API key
2. Data is automatically saved to the `api_data` directory
3. All methods include error handling and logging
4. The API uses colorful console output for better visibility
5. Rate limiting is handled automatically
