from src.data.helius_client import HeliusClient
import asyncio

async def test_helius_api():
    client = HeliusClient()
    token = '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'
    
    # Test RPC endpoint
    print("Testing RPC endpoint...")
    price = client.get_token_price(token)
    print(f'Token price: {price}')
    
    # Test token data
    print("\nTesting token data...")
    df = client.get_token_data(token)
    print(df.head())
    
    # Test WebSocket connection
    print("\nTesting WebSocket connection...")
    async def callback(data):
        print(f"Received update: {data}")
        
    try:
        await asyncio.wait_for(
            client.subscribe_token_updates(token, callback),
            timeout=10
        )
    except asyncio.TimeoutError:
        print("WebSocket test completed (timeout as expected)")

if __name__ == "__main__":
    asyncio.run(test_helius_api())
