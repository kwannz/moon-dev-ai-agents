import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.tweet_agent import TweetAgent

def test_twitter_functionality():
    agent = TweetAgent()
    test_text = 'Testing Moon Dev trading system with real market data from Helius API. Market analysis and trading decisions are now powered by real-time data.'
    tweets = agent.generate_tweets(test_text)
    
    if tweets:
        print("\n✅ Twitter functionality test passed")
        print(f"Generated tweets saved to: {agent.output_file}")
    else:
        print("\n❌ Twitter functionality test failed")

if __name__ == "__main__":
    test_twitter_functionality()
