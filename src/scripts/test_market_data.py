import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data.helius_client import HeliusClient

def test_market_data():
    print("🔍 Testing Helius API market data...")
    client = HeliusClient()
    token = '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'
    
    try:
        data = client.get_token_data(token)
        print(f"\n📊 Token data for {token}:")
        print(data)
        
        price = client.get_token_price(token)
        print(f"\n💰 Token price: ${price:.6f}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error fetching market data: {str(e)}")
        return False

if __name__ == "__main__":
    test_market_data()
