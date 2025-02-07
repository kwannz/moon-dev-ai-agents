import pandas as pd
from datetime import datetime

# Create current_portfolio.csv
portfolio_df = pd.DataFrame({
    'token_address': ['EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'],
    'amount': [0],
    'usd_value': [0],
    'timestamp': ['2025-02-07T00:00:00Z']
})
portfolio_df.to_csv('src/data/portfolio/current_portfolio.csv', index=False)

# Create portfolio_balance.csv
balance_df = pd.DataFrame({
    'token_address': ['EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'],
    'balance': [0],
    'timestamp': ['2025-02-07T00:00:00Z']
})
balance_df.to_csv('src/data/portfolio/portfolio_balance.csv', index=False)
