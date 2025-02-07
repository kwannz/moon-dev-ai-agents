# Lumix AI Trading System ✨

A real-time trading system powered by Helius API and Jupiter V6 Swap API for Solana trading, with AI-driven decision making using the DeepSeek R1 1.5B model.

## System Requirements
- Python 3.10.9
- Ollama server for AI model
- Solana wallet with SOL balance
- Linux/Unix environment

## Quick Start Guide

1. Clone and setup:
   ```bash
   git clone <repository-url>
   cd moon-dev-ai-agents
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env_example .env
   ```
   Required environment variables:
   - HELIUS_API_KEY: For market data (from https://dev.helius.xyz)
   - SOLANA_PRIVATE_KEY: Your wallet's private key for trading
   - COINGECKO_API_KEY: For additional market data

3. Start Ollama server and pull model:
   ```bash
   ollama serve
   ollama pull deepseek-coder:1.5b
   ```

4. Verify wallet balance:
   ```bash
   python3 -c "from src.data.helius_client import HeliusClient; print(f'Wallet Balance: {HeliusClient().get_wallet_balance(\"4BKPzFyjBaRP3L1PNDf3xTerJmbbxxESmDmZJ2CZYdQ5\")} SOL')"
   ```

## Ollama Server Setup
1. Install Ollama: Follow instructions at https://ollama.ai/
2. Pull the DeepSeek R1 1.5B model:
   ```bash
   ollama pull deepseek-coder:1.5b
   ```
3. Start Ollama server:
   ```bash
   ollama serve
   ```
4. The system will automatically connect to http://localhost:11434/api

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

## Trading Configuration
- Default slippage: 2.5% (configurable in config.py)
- Maximum position size: 20% of wallet balance
- Cash buffer: 30% maintained for fees
- Stop loss: -5% with trailing stop
- Technical analysis: Using pandas_ta library

## Running the System

1. Start the trading system:
   ```bash
   python3 src/main.py
   ```
   The system will:
   - Connect to Ollama API with deepseek-r1:1.5b model
   - Initialize all trading agents
   - Start real-time market monitoring
   - Begin executing trades based on AI analysis

2. Active Agents:
   - Risk Agent: Portfolio risk management and balance monitoring
   - Trading Agent: AI-powered trading decisions using DeepSeek model
   - Strategy Agent: Technical analysis and strategy execution
   - CopyBot Agent: Portfolio tracking and performance monitoring
   - Sentiment Agent: Market sentiment analysis and trend detection

3. System Features:
   - Real-time wallet balance monitoring
   - Market data from Helius API
   - AI-powered trading with DeepSeek R1 1.5B
   - Risk management and position sizing
   - Technical analysis using pandas_ta

4. Monitoring Output:
   - Wallet balance and portfolio status
   - Risk management alerts
   - Trading signals and execution
   - Market data updates
   - Agent status messages

## License
MIT License
