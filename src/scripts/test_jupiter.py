import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data.jupiter_client import JupiterClient
from src.config import USDC_ADDRESS, SOL_ADDRESS
from termcolor import cprint

def test_jupiter_integration():
    try:
        client = JupiterClient()
        
        # Test quote
        cprint("\n🔍 Testing Jupiter quote API...", "cyan")
        # Test SOL -> USDC quote (0.1 SOL)
        quote = client.get_quote(
            input_mint="So11111111111111111111111111111111111111112",  # Native SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount=100000000  # 0.1 SOL in lamports
        )
        
        if quote:
            cprint("\n📊 Quote response:", "green")
            print(quote)
            cprint("\n✅ Jupiter API integration test passed", "green")
            return True
        else:
            cprint("\n❌ Jupiter API integration test failed", "red")
            return False
            
    except Exception as e:
        cprint(f"\n❌ Test failed with error: {str(e)}", "red")
        return False

if __name__ == "__main__":
    test_jupiter_integration()
