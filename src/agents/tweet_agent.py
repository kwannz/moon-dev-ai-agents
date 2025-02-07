"""
Lumix Tweet Generator

This agent takes text input and generates tweets based on the content.
"""

import os
import pandas as pd
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import traceback
from src.models import model_factory
import math
from termcolor import colored, cprint
import sys

# Model override settings
# Set to "0" to use config.py's AI_MODEL setting
# Available models:
# - "deepseek-chat" (DeepSeek's V3 model - fast & efficient)
# - "deepseek-reasoner" (DeepSeek's R1 reasoning model)
# - "0" (Use config.py's AI_MODEL setting)
MODEL_OVERRIDE = "deepseek-chat"  # Set to "0" to disable override
DEEPSEEK_BASE_URL = "https://api.deepseek.com"  # Base URL for DeepSeek API

# Text Processing Settings
MAX_CHUNK_SIZE = 10000  # Maximum characters per chunk
TWEETS_PER_CHUNK = 3   # Number of tweets to generate per chunk
USE_TEXT_FILE = True   # Whether to use og_tweet_text.txt by default
# if the above is true, then the below is the file to use
OG_TWEET_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data/tweets/og_tweet_text.txt')

# Import block moved to top of file

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# AI Settings - Override config.py if set
from src import config

# Only set these if you want to override config.py settings
AI_MODEL = False  # Set to model name to override config.AI_MODEL
AI_TEMPERATURE = 0  # Set > 0 to override config.AI_TEMPERATURE
AI_MAX_TOKENS = 150  # Set > 0 to override config.AI_MAX_TOKENS

# Tweet Generation Prompt
TWEET_PROMPT = """Here is a chunk of transcript or text. Please generate three tweets for that text.
Use the below manifest to understand how to speak in the tweet.
Don't use emojis or any corny stuff!
Don't number the tweets - just separate them with blank lines.

Text to analyze:
{text}

Manifest:
- Keep it casual and concise
- Focus on key insights and facts
- no emojis
- always be kind
- No hashtags unless absolutely necessary
- Maximum 280 characters per tweet
- no capitalization
- don't number the tweets
- separate tweets with blank lines

EACH TWEET MUST BE A COMPLETE TAKE AND BE INTERESTING
"""

# Color settings for terminal output
TWEET_COLORS = [
    {'text': 'white', 'bg': 'on_green'},
    {'text': 'white', 'bg': 'on_blue'},
    {'text': 'white', 'bg': 'on_red'}
]

class TweetAgent:
    """Lumix Tweet Generator"""
    
    def __init__(self):
        """Initialize the Tweet Agent"""
        load_dotenv()
        
        # Check Twitter configuration
        self.twitter_enabled = os.getenv('TWITTER_ENABLED', 'true').lower() == 'true'
        if not self.twitter_enabled:
            print("⚠️ Twitter functionality is disabled")
            return
            
        self.twitter_username = os.getenv('TWITTER_USERNAME')
        self.twitter_password = os.getenv('TWITTER_PASSWORD')
        self.twitter_email = os.getenv('TWITTER_EMAIL')
        
        if not all([self.twitter_username, self.twitter_password, self.twitter_email]):
            raise ValueError("Twitter credentials not properly configured")
            
        # Set AI parameters - use config values unless overridden
        self.ai_model = MODEL_OVERRIDE if MODEL_OVERRIDE != "0" else config.AI_MODEL
        self.ai_temperature = AI_TEMPERATURE if AI_TEMPERATURE > 0 else config.AI_TEMPERATURE
        self.ai_max_tokens = AI_MAX_TOKENS if AI_MAX_TOKENS > 0 else config.AI_MAX_TOKENS
        
        print(f"🤖 Using AI Model: {self.ai_model}")
        if AI_MODEL or AI_TEMPERATURE > 0 or AI_MAX_TOKENS > 0:
            print("⚠️ Note: Using some override settings instead of config.py defaults")
            if AI_MODEL:
                print(f"  - Model: {AI_MODEL}")
            if AI_TEMPERATURE > 0:
                print(f"  - Temperature: {AI_TEMPERATURE}")
            if AI_MAX_TOKENS > 0:
                print(f"  - Max Tokens: {AI_MAX_TOKENS}")
        
        load_dotenv()
        
        # Initialize Ollama model
        self.model = None
        max_retries = 3
        retry_count = 0
        
        while self.model is None and retry_count < max_retries:
            try:
                self.model = model_factory.get_model("ollama", "deepseek-r1:1.5b")
                if not self.model:
                    raise ValueError("Could not initialize Ollama model")
            except Exception as e:
                print(f"⚠️ Error initializing model (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(1)  # Wait before retrying
                else:
                    raise ValueError(f"Failed to initialize model after {max_retries} attempts")
        
        # Create tweets directory if it doesn't exist
        self.tweets_dir = Path(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data/tweets'))
        self.tweets_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = self.tweets_dir / f"generated_tweets_{timestamp}.txt"
        
    def _chunk_text(self, text):
        """Split text into chunks of MAX_CHUNK_SIZE characters"""
        return [text[i:i + MAX_CHUNK_SIZE] 
                for i in range(0, len(text), MAX_CHUNK_SIZE)]
    
    def _get_input_text(self, text=None):
        """Get input text from either file or direct input"""
        if USE_TEXT_FILE:
            try:
                with open(OG_TWEET_FILE, 'r') as f:
                    return f.read()
            except Exception as e:
                print(f"❌ Error reading text file: {str(e)}")
                print("⚠️ Falling back to direct text input if provided")
                
        return text
    
    def _print_colored_tweet(self, tweet, color_idx):
        """Print tweet with color based on its position"""
        color_settings = TWEET_COLORS[color_idx % len(TWEET_COLORS)]
        cprint(tweet, color_settings['text'], color_settings['bg'])
        print()  # Add spacing between tweets
    
    def generate_tweets(self, text=None):
        """Generate tweets from text input or file"""
        if not hasattr(self, 'twitter_enabled') or not self.twitter_enabled:
            print("⚠️ Twitter functionality is disabled")
            return None
            
        try:
            if not all([self.twitter_username, self.twitter_password, self.twitter_email]):
                print("❌ Twitter credentials not properly configured")
                return None
                
            # Get input text
            input_text = self._get_input_text(text)
            
            if not input_text:
                print("❌ No input text provided and couldn't read from file")
                return None
            
            # Calculate and display text stats
            total_chars = len(input_text)
            total_chunks = math.ceil(total_chars / MAX_CHUNK_SIZE)
            total_tweets = total_chunks * TWEETS_PER_CHUNK
            
            print(f"\n📊 Text Analysis:")
            print(f"Total characters: {total_chars:,}")
            print(f"Chunk size: {MAX_CHUNK_SIZE:,}")
            print(f"Number of chunks: {total_chunks:,}")
            print(f"Tweets per chunk: {TWEETS_PER_CHUNK}")
            print(f"Total tweets to generate: {total_tweets:,}")
            print("=" * 50)
            
            # Split text into chunks if needed
            chunks = self._chunk_text(input_text)
            all_tweets = []
            
            for i, chunk in enumerate(chunks, 1):
                print(f"\n🔄 Processing chunk {i}/{total_chunks} ({len(chunk):,} characters)")
                
                # Prepare the context
                context = TWEET_PROMPT.format(text=chunk)
                
                # Get tweets using Ollama
                if self.model is None:
                    print("⚠️ Model not initialized, skipping tweet generation")
                    continue
                    
                try:
                    response = self.model.generate_response(
                        system_prompt="You are Lumix Tweet Generator. Generate tweets based on the provided text.",
                        user_content=context,
                        temperature=self.ai_temperature
                    )
                except Exception as e:
                    print(f"❌ Error generating tweets: {str(e)}")
                    continue
                if not response:
                    print("❌ Failed to get model response")
                    continue
                    
                response_text = str(response)
                
                # Parse tweets from response and remove any numbering
                chunk_tweets = []
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line:
                        # Remove any leading numbers (1., 2., etc.)
                        cleaned_line = line.lstrip('0123456789. ')
                        if cleaned_line:
                            chunk_tweets.append(cleaned_line)
                
                # Print tweets with colors to terminal
                print("\n🐦 Generated tweets for this chunk:")
                for idx, tweet in enumerate(chunk_tweets):
                    self._print_colored_tweet(tweet, idx)
                
                all_tweets.extend(chunk_tweets)
                
                # Write tweets to file with paragraph spacing (clean format)
                try:
                    with open(self.output_file, 'a') as f:
                        for tweet in chunk_tweets:
                            f.write(f"{tweet}\n\n")  # Double newline for paragraph spacing
                except Exception as e:
                    print(f"❌ Error writing tweets to file: {str(e)}")
                    # Continue execution even if file write fails
                
                # Small delay between chunks to avoid rate limits
                if i < total_chunks:
                    time.sleep(1)
            
            return all_tweets
            
        except Exception as e:
            print(f"❌ Error generating tweets: {str(e)}")
            traceback.print_exc()
            return None

if __name__ == "__main__":
    agent = TweetAgent()
    
    # Example usage with direct text
    test_text = """Bitcoin showing strong momentum with increasing volume. 
    Price action suggests accumulation phase might be complete. 
    Key resistance at $69,000 with support holding at $65,000."""
    
    # If USE_TEXT_FILE is True, it will use the file instead of test_text
    tweets = agent.generate_tweets(test_text)
    
    if tweets:
        print(f"\nTweets have been saved to: {agent.output_file}")
