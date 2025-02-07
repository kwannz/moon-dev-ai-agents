import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data.helius_client import HeliusClient
from termcolor import cprint

def test_wallet_balance():
    try:
        client = HeliusClient()
        wallet_address = "4BKPzFyjBaRP3L1PNDf3xTerJmbbxxESmDmZJ2CZYdQ5"
        
        # Get SOL balance
        balance = client.get_wallet_balance(wallet_address)
        
        cprint(f"\n💰 Wallet Balance:", "cyan")
        cprint(f"Address: {wallet_address}", "cyan")
        cprint(f"SOL Balance: {balance:.6f} SOL", "green")
        
        return True
    except Exception as e:
        cprint(f"\n❌ Failed to get wallet balance: {str(e)}", "red")
        return False

if __name__ == "__main__":
    test_wallet_balance()
