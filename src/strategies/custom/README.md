# Lumix Custom Strategies Directory

This directory is for your trading strategies. Strategies with certain filename prefixes will be automatically ignored by git to keep them private.

## Private Strategy Naming
To keep a strategy private (not tracked by git), prefix the filename with:
- `private_` (e.g., `private_my_strategy.py`)
- `secret_` (e.g., `secret_alpha_strat.py`) 
- `dev_` (e.g., `dev_test_strat.py`)

These patterns are included in `.gitignore` so your private strategies won't be committed to the repository.

## Creating a Custom Strategy

1. Create a new Python file in this directory (e.g., `private_my_strategy.py`)
2. Import and inherit from the base strategy class:
```python
from ..base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("My Strategy Name")
        # Your initialization code here
    
    def generate_signals(self) -> dict:
        # Your strategy logic here
        return {
            'token': 'token_address',
            'signal': 0.85,        # 0-1 strength
            'direction': 'BUY',    # 'BUY', 'SELL', or 'NEUTRAL'
            'metadata': {
                'your_custom_data': 'here'
            }
        }
```

## Required Signal Format
- `token`: Token address (string)
- `signal`: Signal strength between 0-1 (float)
- `direction`: Must be 'BUY', 'SELL', or 'NEUTRAL' (string)
- `metadata`: Optional dictionary with strategy-specific data

## Example Metadata Fields
```python
metadata = {
    'strategy_type': 'mean_reversion',
    'indicators': {
        'rsi': 28,
        'macd': 'bullish',
        'volume': 'above_average'
    },
    'confidence_factors': {
        'price_action': True,
        'volume_confirms': True
    },
    'analysis': {
        'support_level': 1.23,
        'resistance_level': 1.45
    }
}
```

## Tips
- Use the naming patterns above to keep strategies private
- Use the example strategy as a template
- Implement proper error handling
- Add detailed metadata for better LLM analysis
- Use utility functions from nice_funcs.py

## Security Notes
- Never commit API keys or private keys in any file
- Use environment variables for sensitive data
- Double check your strategy filenames before committing

## Questions?
Check out the example strategy for help!  