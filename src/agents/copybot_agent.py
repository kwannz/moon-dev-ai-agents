"""
CopyBot Agent
Analyzes current portfolio positions to identify opportunities for increased position sizes.
Monitors OHLCV data and market structure to make informed position sizing decisions.
"""

import os
import pandas as pd
from termcolor import colored, cprint
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
from src.config import *
from src import nice_funcs as n
from src.data.ohlcv_collector import collect_all_tokens, collect_token_data
from src.models import ModelFactory

# Data path for current copybot portfolio
COPYBOT_PORTFOLIO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data/portfolio/current_portfolio.csv')

# LLM Prompts
PORTFOLIO_ANALYSIS_PROMPT = """
You are the CopyBot Agent

Your task is to analyze the current copybot portfolio positions and market data to identify which positions deserve larger allocations.

Data provided:
1. Current copybot portfolio positions and their performance
2. OHLCV market data for each position
3. Technical indicators (MA20, MA40, ABOVE OR BELOW)

Analysis Criteria:
1. Position performance metrics
2. Price action and momentum
3. Volume analysis
4. Risk/reward ratio
5. Market conditions

{portfolio_data}
{market_data}

Respond in this exact format:
1. First line must be one of: BUY, SELL, or NOTHING (in caps)
2. Then explain your reasoning, including:
   - Position analysis
   - Technical analysis
   - Volume profile
   - Risk assessment
   - Market conditions
   - Confidence level (as a percentage, e.g. 75%)

Remember: 
- Do not worry about the low position size of the copybot, but more so worry about the size vs the others in the portfolio. this copy bot acts as a scanner for you to see what type of opportunties are out there and trending. 
- Look for high-conviction setups
- Consider both position performance against others in the list and market conditions
"""

class CopyBotAgent:
    """CopyBot Agent for portfolio analysis"""
    
    def __init__(self):
        """Initialize the CopyBot agent with LLM"""
        load_dotenv()
        self.model = None
        max_retries = 3
        retry_count = 0
        
        while self.model is None and retry_count < max_retries:
            try:
                self.model_factory = ModelFactory()
                self.model = self.model_factory.get_model("ollama")
                if not self.model:
                    raise ValueError("Could not initialize Ollama model")
            except Exception as e:
                print(f"⚠️ Error initializing model (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(1)  # Wait before retrying
                else:
                    raise ValueError(f"Failed to initialize model after {max_retries} attempts")
                    
        self.recommendations_df = pd.DataFrame(columns=['token', 'action', 'confidence', 'reasoning'])
        print("CopyBot Agent initialized!")
        
    def load_portfolio_data(self):
        """Load current copybot portfolio data"""
        try:
            if not os.path.exists(COPYBOT_PORTFOLIO_PATH):
                print(f"❌ Portfolio file not found: {COPYBOT_PORTFOLIO_PATH}")
                return False
                
            self.portfolio_df = pd.read_csv(COPYBOT_PORTFOLIO_PATH)
            print("💼 Current copybot portfolio loaded!")
            print(self.portfolio_df)
            return True
        except Exception as e:
            print(f"❌ Error loading portfolio data: {str(e)}")
            return False
            
    def analyze_position(self, token):
        """Analyze a single portfolio position"""
        try:
            if token in EXCLUDED_TOKENS:
                print(f"⚠️ Skipping analysis for excluded token: {token}")
                return None
                
            # Get position data
            position_data = self.portfolio_df[self.portfolio_df['Mint Address'] == token]
            if position_data.empty:
                print(f"⚠️ No portfolio data for token: {token}")
                return None
                
            print(f"\n🔍 Analyzing position for {position_data['name'].values[0]}...")
            print(f"💰 Current Amount: {position_data['Amount'].values[0]}")
            print(f"💵 USD Value: ${position_data['USD Value'].values[0]:.2f}")
                
            # Get OHLCV data - Use collect_token_data instead of collect_all_tokens
            print("\n📊 Fetching OHLCV data...")
            try:
                token_market_data = collect_token_data(token)
                print("\n🔍 OHLCV Data Retrieved:")
                if token_market_data is None or token_market_data.empty:
                    print("❌ No OHLCV data found")
                    token_market_data = "No market data available"
                else:
                    print("✅ OHLCV data found:")
                    print("Shape:", token_market_data.shape)
                    print("\nFirst few rows:")
                    print(token_market_data.head())
                    print("\nColumns:", token_market_data.columns.tolist())
            except Exception as e:
                print(f"❌ Error collecting OHLCV data: {str(e)}")
                token_market_data = "No market data available"
            
            # Prepare context for LLM
            full_prompt = f"""
{PORTFOLIO_ANALYSIS_PROMPT.format(
    portfolio_data=position_data.to_string(),
    market_data=token_market_data
)}
"""
            print("\n📝 Full Prompt Being Sent to LLM:")
            print("=" * 80)
            print(full_prompt)
            print("=" * 80)
            
            print("\nSending data for analysis...")
            
            # Get LLM analysis
            if self.model is None:
                print("⚠️ Model not initialized, skipping AI analysis")
                return None
                
            try:
                response = self.model.generate_response(
                    system_prompt="You are the CopyBot Agent. Analyze portfolio positions and market data.",
                    user_content=full_prompt,
                    temperature=AI_TEMPERATURE
                )
            except Exception as e:
                print(f"❌ Error getting AI analysis: {str(e)}")
                return None
            if not response:
                return None
                
            response_text = str(response)
            print("\n🎯 AI Analysis Results:")
            print("=" * 50)
            print(response_text)
            print("=" * 50)
            
            lines = response_text.split('\n')
            action = lines[0].strip() if lines else "NOTHING"
            
            # Extract confidence
            confidence = 0
            for line in lines:
                if 'confidence' in line.lower():
                    try:
                        confidence = int(''.join(filter(str.isdigit, line)))
                    except:
                        confidence = 50
            
            # Store recommendation
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else "No detailed reasoning provided"
            self.recommendations_df = pd.concat([
                self.recommendations_df,
                pd.DataFrame([{
                    'token': token,
                    'action': action,
                    'confidence': confidence,
                    'reasoning': reasoning
                }])
            ], ignore_index=True)
            
            print(f"\n📊 Summary for {position_data['name'].values[0]}:")
            print(f"Action: {action}")
            print(f"Confidence: {confidence}%")
            print(f"🎯 Position Analysis Complete!")
            return response
            
        except Exception as e:
            print(f"❌ Error analyzing position: {str(e)}")
            return None
            
    def execute_position_updates(self):
        """Execute position size updates based on analysis"""
        try:
            print("\nExecuting position updates...")
            
            for _, row in self.recommendations_df.iterrows():
                token = row['token']
                action = row['action']
                confidence = row['confidence']
                
                # instead of try/excempt it just looks for nothing and continues
                # if action == "NOTHING" or token in EXCLUDED_TOKENS:
                #     continue
                    
                if confidence < STRATEGY_MIN_CONFIDENCE:
                    print(f"⚠️ Skipping {token}: Confidence {confidence}% below threshold")
                    continue
                
                print(f"\n🎯 Processing {action} for {token}...")
                
                try:
                    # Get current position value
                    current_position = n.get_token_balance_usd(token)
                    
                    if action == "BUY":
                        # Calculate position size based on confidence
                        max_position = usd_size * (MAX_POSITION_PERCENTAGE / 100)
                        target_size = max_position * (confidence / 100)
                        
                        print(f"💰 Current Position: ${current_position:.2f}")
                        print(f"🎯 Target Size: ${target_size:.2f}")
                        
                        # Calculate difference
                        amount_to_buy = target_size - current_position
                        
                        if amount_to_buy <= 0:
                            print(f"✨ Already at or above target size! (${current_position:.2f} > ${target_size:.2f})")
                            continue
                            
                        print(f"🛍️ Buying ${amount_to_buy:.2f} of {token}")
                        
                        # Execute the buy using nice_funcs
                        success = n.ai_entry(
                            token,
                            amount_to_buy
                        )
                        
                        if success:
                            print(f"✅ Successfully bought {token}")
                        else:
                            print(f"❌ Trade execution failed for {token}")
                                
                    elif action == "SELL":
                        if current_position > 0:
                            print(f"💰 Selling position worth ${current_position:.2f}")
                            
                            # Execute the sell using nice_funcs
                            success = n.chunk_kill(
                                token,
                                max_usd_order_size,  # From config.py
                                slippage  # From config.py
                            )
                            
                            if success:
                                print(f"✅ Successfully sold {token}")
                            else:
                                print(f"❌ Failed to sell {token}")
                        else:
                            print("ℹ️ No position to sell")
                    
                    # Sleep between trades
                    time.sleep(tx_sleep)
                    
                except Exception as e:
                    print(f"❌ Error executing trade for {token}: {str(e)}")
                    continue
                
        except Exception as e:
            print(f"❌ Error updating positions: {str(e)}")
            
    def run_analysis_cycle(self):
        """Run a complete portfolio analysis cycle"""
        try:
            print("\nStarting CopyBot Portfolio Analysis...")
            
            # Load portfolio data
            if not self.load_portfolio_data():
                return
                
            # Get unique tokens from portfolio
            portfolio_tokens = self.portfolio_df['Mint Address'].unique()
            
            # Reset recommendations for new cycle
            self.recommendations_df = pd.DataFrame(columns=['token', 'action', 'confidence', 'reasoning'])
            
            # Analyze each position
            for token in portfolio_tokens:
                self.analyze_position(token)
                
            # Print all recommendations
            if not self.recommendations_df.empty:
                print("\n📊 All Position Recommendations:")
                print("=" * 80)
                for _, rec in self.recommendations_df.iterrows():
                    token_name = self.portfolio_df[self.portfolio_df['Mint Address'] == rec['token']]['name'].values[0]
                    print(f"\n🪙 Token: {token_name}")
                    print(f"💼 Address: {rec['token']}")
                    print(f"🎯 Action: {rec['action']}")
                    print(f"📊 Confidence: {rec['confidence']}%")
                    print("\n📝 Full Analysis:")
                    print("-" * 40)
                    print(rec['reasoning'])
                    print("-" * 40)
                print("=" * 80)
            
            # Execute position updates
            self.execute_position_updates()
            
            print("\n✨ Portfolio analysis cycle complete!")
            
        except Exception as e:
            print(f"❌ Error in analysis cycle: {str(e)}")

if __name__ == "__main__":
    analyzer = CopyBotAgent()
    analyzer.run_analysis_cycle()
