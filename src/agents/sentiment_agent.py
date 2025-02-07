'''
Sentiment Agent
Monitors Twitter sentiment for token list using twikit.
Analyzes sentiment using HuggingFace models and tracks mentioned tokens.

Required:
1. First run twitter_login.py to generate cookies located: src/scripts/twitter_login.py
    - this will save a cookies.json that you should not share. make sure its in .gitignore
2. Make sure your .env has the Twitter credentials, example added to .env.example
'''

# Configuration
TOKENS_TO_TRACK = ["solana", "bitcoin", "ethereum"]  # Add tokens you want to track
TWEETS_PER_RUN = 30  # Number of tweets to collect per run
DATA_FOLDER = "src/data/sentiment"  # Where to store sentiment data
SENTIMENT_HISTORY_FILE = "src/data/sentiment_history.csv"  # Store sentiment scores over time
IGNORE_LIST = ['t.co', 'discord', 'join', 'telegram', 'discount', 'pay']
CHECK_INTERVAL_MINUTES = 15  # How often to run sentiment analysis

# Sentiment settings
SENTIMENT_ANNOUNCE_THRESHOLD = 0.4  # Announce vocally if abs(sentiment) > this value (-1 to 1 scale)

# Voice settings (copied from whale agent)
VOICE_MODEL = "tts-1"  # or tts-1-hd for higher quality
VOICE_NAME = "nova"   # Options: alloy, echo, fable, onyx, nova, shimmer
VOICE_SPEED = 1      # 0.25 to 4.0

import httpx
from dotenv import load_dotenv
import os
import sys
from termcolor import cprint
import time
from datetime import datetime, timedelta
import csv 
from random import randint
import pathlib
import asyncio
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import openai
from pathlib import Path

# Create data directory if it doesn't exist
pathlib.Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv()

# Get OpenAI key for voice
openai.api_key = os.getenv("OPENAI_KEY")

# Patch httpx
original_client = httpx.Client
def patched_client(*args, **kwargs):
    # Add browser-like headers
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    
    # List of common user agents
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    ]
    
    kwargs['headers'].update({
        'User-Agent': user_agents[randint(0, len(user_agents)-1)],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"'
    })
    
    kwargs.pop('proxy', None)
    return original_client(*args, **kwargs)

httpx.Client = patched_client

# imports
from .base_agent import BaseAgent

class SentimentAgent(BaseAgent):
    def __init__(self):
        """Initialize the Sentiment Agent"""
        super().__init__("sentiment")
        self.tokenizer = None
        self.model = None
        self.audio_dir = Path("src/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize sentiment history file
        if not os.path.exists(SENTIMENT_HISTORY_FILE):
            pd.DataFrame(columns=['timestamp', 'sentiment_score', 'num_tweets']).to_csv(SENTIMENT_HISTORY_FILE, index=False)
        
        # Load the sentiment model at initialization
        cprint("🤖 Loading sentiment model...", "cyan")
        try:
            self.init_sentiment_model()
            cprint("✨ Sentiment model loaded!", "green")
        except Exception as e:
            cprint(f"⚠️ Error loading sentiment model: {str(e)}", "yellow")
            self.tokenizer = None
            self.model = None
        cprint("Sentiment Agent initialized! (Twitter functionality disabled)", "green")
        
    def init_sentiment_model(self):
        """Initialize the BERT model for sentiment analysis"""
        try:
            if self.tokenizer is None or self.model is None:
                self.tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
                self.model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
                return True
            return False
        except Exception as e:
            cprint(f"❌ Error loading sentiment model: {str(e)}", "red")
            raise

    def analyze_sentiment(self, texts):
        """Analyze sentiment of a batch of texts"""
        if not texts:
            return 0.0
            
        try:
            if self.tokenizer is None or self.model is None:
                try:
                    self.init_sentiment_model()
                except Exception:
                    cprint("⚠️ Could not initialize sentiment model, returning neutral sentiment", "yellow")
                    return 0.0
                    
            if self.tokenizer is None or self.model is None:
                cprint("⚠️ Model initialization failed, returning neutral sentiment", "yellow")
                return 0.0
                
            sentiments = []
            batch_size = 8  # Process in small batches to avoid memory issues
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                inputs = self.tokenizer(batch_texts, padding=True, truncation=True, max_length=128, return_tensors="pt")
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    sentiments.extend(predictions.tolist())
                    
            return self._calculate_sentiment_scores(sentiments)
        except Exception as e:
            cprint(f"❌ Error analyzing sentiment: {str(e)}", "red")
            return 0.0  # Return neutral sentiment on error
        
    def _calculate_sentiment_scores(self, sentiments):
        """Convert sentiment predictions to scores"""
        scores = []
        for sentiment in sentiments:
            # NEG, NEU, POS
            neg, neu, pos = sentiment
            # Convert to -1 to 1 scale
            score = pos - neg  # Will be between -1 and 1
            scores.append(score)
            
        return np.mean(scores)

    def _announce(self, message, is_important=False):
        """Announce a message using text-to-speech"""
        try:
            print(f"\n🗣️ {message}")
            
            # Only use voice for important messages
            if not is_important:
                return
                
            # Generate unique filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            speech_file = self.audio_dir / f"sentiment_audio_{timestamp}.mp3"
            
            # Generate speech using OpenAI
            response = openai.audio.speech.create(
                model=VOICE_MODEL,
                voice=VOICE_NAME,
                speed=VOICE_SPEED,
                input=message
            )
            
            # Save and play the audio
            with open(speech_file, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            
            # Play the audio
            if os.name == 'posix':  # macOS/Linux
                os.system(f"afplay {speech_file}")
            else:  # Windows
                os.system(f"start {speech_file}")
                time.sleep(5)
            
            # Clean up
            try:
                speech_file.unlink()
            except Exception as e:
                print(f"⚠️ Couldn't delete audio file: {e}")
                
        except Exception as e:
            print(f"❌ Error in text-to-speech: {str(e)}")

    def save_sentiment_score(self, sentiment_score, num_tweets):
        """Save sentiment score to history"""
        try:
            new_data = pd.DataFrame([{
                'timestamp': datetime.now().isoformat(),
                'sentiment_score': sentiment_score,
                'num_tweets': num_tweets
            }])
            
            # Load existing data
            if os.path.exists(SENTIMENT_HISTORY_FILE):
                history_df = pd.read_csv(SENTIMENT_HISTORY_FILE)
                # Convert timestamps to datetime for comparison
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
                # Keep only last 24 hours of data
                cutoff_time = datetime.now() - timedelta(hours=24)
                history_df = history_df[history_df['timestamp'] > cutoff_time]
                # Convert back to ISO format for consistent storage
                history_df['timestamp'] = history_df['timestamp'].apply(lambda x: x.isoformat())
                # Append new data
                history_df = pd.concat([history_df, new_data], ignore_index=True)
            else:
                history_df = new_data
                
            history_df.to_csv(SENTIMENT_HISTORY_FILE, index=False)
            
        except Exception as e:
            cprint(f"❌ Error saving sentiment history: {str(e)}", "red")

    def get_sentiment_change(self):
        """Calculate sentiment change from last run"""
        try:
            if not os.path.exists(SENTIMENT_HISTORY_FILE):
                return None, None
                
            history_df = pd.read_csv(SENTIMENT_HISTORY_FILE)
            if len(history_df) < 2:
                return None, None
                
            # Convert timestamps using ISO format
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], format='ISO8601')
            history_df = history_df.sort_values('timestamp')
            
            current_score = float(history_df.iloc[-1]['sentiment_score'])
            previous_score = float(history_df.iloc[-2]['sentiment_score'])
            
            # Calculate time difference in minutes
            time_diff = (history_df.iloc[-1]['timestamp'] - history_df.iloc[-2]['timestamp']).total_seconds() / 60
            
            # Calculate percentage change relative to the scale (-1 to 1)
            # Convert to 0-100 scale for easier understanding
            current_percent = (current_score + 1) * 50
            previous_percent = (previous_score + 1) * 50
            percent_change = current_percent - previous_percent
            
            return percent_change, time_diff
            
        except Exception as e:
            cprint(f"❌ Error calculating sentiment change: {str(e)}", "red")
            return None, None

    def analyze_and_announce_sentiment(self, tweets):
        """Analyze sentiment of tweets and announce results"""
        if not tweets:
            return
            
        # Extract text from tweets
        texts = [tweet.text for tweet in tweets]
        
        # Get sentiment score
        sentiment_score = self.analyze_sentiment(texts)
        
        # Save score to history
        self.save_sentiment_score(sentiment_score, len(texts))
        
        # Get change since last run
        percent_change, time_diff = self.get_sentiment_change()
        
        # Convert score to human readable format
        if sentiment_score > 0.3:
            sentiment = "very positive"
        elif sentiment_score > 0:
            sentiment = "slightly positive"
        elif sentiment_score > -0.3:
            sentiment = "slightly negative"
        else:
            sentiment = "very negative"
            
        # Format the score as a percentage for easier understanding
        score_percent = (sentiment_score + 1) * 50  # Convert -1 to 1 into 0 to 100
            
        # Prepare announcement
        message = f"Sentiment Analysis: After analyzing {len(texts)} tweets, "
        message += f"the crypto sentiment is {sentiment} "
        message += f"with a score of {score_percent:.1f} out of 100"
        
        # Add change information if available
        if percent_change is not None and time_diff is not None:
            direction = "up" if percent_change > 0 else "down"
            message += f". Sentiment has moved {direction} {abs(percent_change):.1f} points "
            message += f"over the past {int(time_diff)} minutes"
            
            # Add percentage interpretation
            if abs(percent_change) > 10:
                message += f" - this is a significant {abs(percent_change):.1f}% change!"
            elif abs(percent_change) > 5:
                message += f" - a moderate {abs(percent_change):.1f}% shift"
            else:
                message += f" - a small {abs(percent_change):.1f}% change"
        
        message += "."
        
        # Announce with voice if sentiment is significant or if there's a big change
        is_important = abs(sentiment_score) > SENTIMENT_ANNOUNCE_THRESHOLD or (percent_change is not None and abs(percent_change) > 5)
        self._announce(message, is_important)
        
        # If not announcing vocally, print the raw score for debugging
        if not is_important:
            cprint(f"📊 Raw sentiment score: {sentiment_score:.2f} (on scale of -1 to 1)", "cyan")

    def get_tweets(self, query):
        """Disabled Twitter functionality - returns empty list"""
        cprint("⚠️ Twitter functionality is disabled", "yellow")
        return []

    def save_tweets(self, tweets, token):
        """Save tweets to CSV file using pandas, appending new ones and avoiding duplicates"""
        filename = f"{DATA_FOLDER}/{token}_tweets.csv"
        
        # Prepare new tweets data
        new_tweets_data = []
        for tweet in tweets:
            if not hasattr(tweet, 'id'):
                continue
                
            try:
                tweet_data = {
                    "collection_time": datetime.now().isoformat(),
                    "tweet_id": str(tweet.id),
                    "created_at": tweet.created_at,
                    "user_name": tweet.user.name,
                    "user_id": str(tweet.user.id),
                    "text": tweet.text,
                    "retweet_count": tweet.retweet_count,
                    "favorite_count": tweet.favorite_count,
                    "reply_count": tweet.reply_count,
                    "quote_count": getattr(tweet, 'quote_count', 0),
                    "language": getattr(tweet, 'lang', 'unknown')
                }
                new_tweets_data.append(tweet_data)
            except Exception as e:
                cprint(f"⚠️ Error processing tweet: {str(e)}", "yellow")
                continue
        
        if not new_tweets_data:
            cprint("ℹ️ No new tweets to save", "yellow")
            return
            
        # Convert to DataFrame
        new_df = pd.DataFrame(new_tweets_data)
        
        try:
            # Load existing data if file exists
            if os.path.exists(filename):
                existing_df = pd.read_csv(filename)
                # Remove duplicates based on tweet_id
                new_df = new_df[~new_df['tweet_id'].isin(existing_df['tweet_id'])]
                # Append new data
                if not new_df.empty:
                    pd.concat([existing_df, new_df], ignore_index=True).to_csv(filename, index=False)
            else:
                # Save new file
                new_df.to_csv(filename, index=False)
            
            cprint(f"📝 Added {len(new_df)} new tweets to {token}_tweets.csv", "green")
            if os.path.exists(filename):
                total_tweets = len(pd.read_csv(filename))
                cprint(f"📊 Total tweets in database: {total_tweets}", "green")
                
        except Exception as e:
            cprint(f"❌ Error saving to CSV: {str(e)}", "red")

    def run_async(self):
        """Run sentiment analysis (Twitter functionality disabled)"""
        cprint("Sentiment Analysis running...", "cyan")
        cprint("⚠️ Twitter functionality is disabled", "yellow")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
        cprint("Sentiment Analysis complete!", "green")

    def run(self):
        """Main function to run sentiment analysis (implements BaseAgent interface)"""
        self.run_async()  # Run the async implementation while maintaining BaseAgent interface

if __name__ == "__main__":
    try:
        agent = SentimentAgent()
        cprint(f"\nSentiment Agent starting (checking every {CHECK_INTERVAL_MINUTES} minutes)...", "cyan")
        
        while True:
            try:
                agent.run()
                next_run = datetime.now() + timedelta(minutes=CHECK_INTERVAL_MINUTES)
                cprint(f"\n😴 Next sentiment check at {next_run.strftime('%H:%M:%S')}", "cyan")
                time.sleep(60 * CHECK_INTERVAL_MINUTES)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                cprint(f"\n❌ Error in run loop: {str(e)}", "red")
                time.sleep(60)  # Wait a minute before retrying
                
    except KeyboardInterrupt:
        cprint("\nSentiment Agent shutting down gracefully...", "yellow")
    except Exception as e:
        cprint(f"\n❌ Fatal error: {str(e)}", "red")
        sys.exit(1)
