# Lumix AI Trading System ✨

A real-time trading system powered by Helius API and Jupiter V6 Swap API for Solana trading, with AI-driven decision making using the DeepSeek R1 1.5B model.

## Features
- Real-time market data from Helius API
- Automated trading via Jupiter V6 Swap API
- AI-powered trading decisions with DeepSeek R1 1.5B
- Token analysis and risk management
- Portfolio tracking and management

## Setup
1. Copy `.env_example` to `.env` and fill in required API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Run the system: `python src/main.py`

## Configuration
- HELIUS_API_KEY: Required for market data
- SOLANA_PRIVATE_KEY: Required for trading
- DEEPSEEK_KEY: Required for AI model
- Other optional keys in `.env_example`

## Trading Parameters
- Default slippage: 2.5%
- Maximum position size: 20%
- Cash buffer: 30%
- Stop loss: -5%

## License
MIT License
