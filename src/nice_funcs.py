"""
Lumix Trading Functions - A collection of utility functions for trading
"""

from src.config import *
import requests
import pandas as pd
import pprint
import re as reggie
import sys
import os
import time
import json
import numpy as np
import datetime
import pandas_ta as ta
from datetime import datetime, timedelta
from termcolor import colored, cprint
import solders
from dotenv import load_dotenv
import shutil
import atexit
from src.data.helius_client import HeliusClient
from src.data.jupiter_client import JupiterClient

# Constants
MIN_TRADES_LAST_HOUR = 100  # Minimum trades required in last hour
SLIPPAGE = 500  # Default slippage (5%)
STOP_LOSS_PERCENTAGE = -0.05  # Default stop loss percentage (-5%)
USDC_SIZE = float(os.getenv("USDC_SIZE", "10.0"))  # Default USDC size
sell_at_multiple = float(os.getenv("SELL_AT_MULTIPLE", "1.5"))  # Default sell multiple
dont_trade_list = [os.getenv("USDC_ADDRESS", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")]  # List of tokens to not trade
orders_per_open = int(os.getenv("ORDERS_PER_OPEN", "3"))  # Number of orders to place when opening position
tx_sleep = int(os.getenv("TX_SLEEP", "15"))  # Sleep time between transactions
max_usd_order_size = float(os.getenv("MAX_USD_ORDER_SIZE", "1000.0"))  # Maximum order size in USD

# Load environment variables
load_dotenv()

# Get API keys from environment
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
if not BIRDEYE_API_KEY:
    raise ValueError("🚨 BIRDEYE_API_KEY not found in environment variables!")

sample_address = "2yXTyarttn2pTZ6cwt4DqmrRuBw1G7pmFv9oT6MStdKP"

BASE_URL = "https://public-api.birdeye.so/defi"

# Create temp directory and register cleanup
os.makedirs('temp_data', exist_ok=True)

def cleanup_temp_data():
    if os.path.exists('temp_data'):
        print("🧹 Cleaning up temporary data...")
        shutil.rmtree('temp_data')

atexit.register(cleanup_temp_data)

# Custom function to print JSON in a human-readable format
def print_pretty_json(data):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)

# Function to print JSON in a human-readable format - assuming you already have it as print_pretty_json
# Helper function to find URLs in text
def find_urls(string):
    # Regex to extract URLs
    return reggie.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

# UPDATED TO RMEOVE THE OTHER ONE so now we can just use this filter instead of filtering twice
def token_overview(address):
    """
    Fetch token overview for a given address and return structured information, including specific links,
    and assess if any price change suggests a rug pull.
    """

    print(f'Getting the token overview for {address}')
    overview_url = f"{BASE_URL}/token_overview?address={address}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    response = requests.get(overview_url, headers=headers)
    result = {}

    if response.status_code == 200:
        overview_data = response.json().get('data', {})

        # Retrieve buy1h, sell1h, and calculate trade1h
        buy1h = overview_data.get('buy1h', 0)
        sell1h = overview_data.get('sell1h', 0)
        trade1h = buy1h + sell1h

        # Add the calculated values to the result
        result['buy1h'] = buy1h
        result['sell1h'] = sell1h
        result['trade1h'] = trade1h

        # Calculate buy and sell percentages
        total_trades = trade1h  # Assuming total_trades is the sum of buy and sell
        buy_percentage = (buy1h / total_trades * 100) if total_trades else 0
        sell_percentage = (sell1h / total_trades * 100) if total_trades else 0
        result['buy_percentage'] = buy_percentage
        result['sell_percentage'] = sell_percentage

        # Check if trade1h is bigger than MIN_TRADES_LAST_HOUR
        result['minimum_trades_met'] = True if trade1h >= MIN_TRADES_LAST_HOUR else False

        # Extract price changes over different timeframes
        price_changes = {k: v for k, v in overview_data.items() if 'priceChange' in k}
        result['priceChangesXhrs'] = price_changes

        # Check for rug pull indicator
        rug_pull = any(value < -80 for key, value in price_changes.items() if value is not None)
        result['rug_pull'] = rug_pull
        if rug_pull:
            print("Warning: Price change percentage below -80%, potential rug pull")

        # Extract other metrics
        unique_wallet2hr = overview_data.get('uniqueWallet24h', 0)
        v24USD = overview_data.get('v24hUSD', 0)
        watch = overview_data.get('watch', 0)
        view24h = overview_data.get('view24h', 0)
        liquidity = overview_data.get('liquidity', 0)

        # Add the retrieved data to result
        result.update({
            'uniqueWallet2hr': unique_wallet2hr,
            'v24USD': v24USD,
            'watch': watch,
            'view24h': view24h,
            'liquidity': liquidity,
        })

        # Extract and process description links if extensions are not None
        extensions = overview_data.get('extensions', {})
        description = extensions.get('description', '') if extensions else ''
        urls = find_urls(description)
        links = []
        for url in urls:
            if 't.me' in url:
                links.append({'telegram': url})
            elif 'twitter.com' in url:
                links.append({'twitter': url})
            elif 'youtube' not in url:  # Assume other URLs are for website
                links.append({'website': url})

        # Add extracted links to result
        result['description'] = links


        # Return result dictionary with all the data
        return result
    else:
        print(f"Failed to retrieve token overview for address {address}: HTTP status code {response.status_code}")
        return None


def token_security_info(address):

    '''

    bigmatter
​freeze authority is like renouncing ownership on eth

    Token Security Info:
{   'creationSlot': 242801308,
    'creationTime': 1705679481,
    'creationTx': 'ZJGoayaNDf2dLzknCjjaE9QjqxocA94pcegiF1oLsGZ841EMWBEc7TnDKLvCnE8cCVfkvoTNYCdMyhrWFFwPX6R',
    'creatorAddress': 'AGWdoU4j4MGJTkSor7ZSkNiF8oPe15754hsuLmwcEyzC',
    'creatorBalance': 0,
    'creatorPercentage': 0,
    'freezeAuthority': None,
    'freezeable': None,
    'isToken2022': False,
    'isTrueToken': None,
    'lockInfo': None,
    'metaplexUpdateAuthority': 'AGWdoU4j4MGJTkSor7ZSkNiF8oPe15754hsuLmwcEyzC',
    'metaplexUpdateAuthorityBalance': 0,
    'metaplexUpdateAuthorityPercent': 0,
    'mintSlot': 242801308,
    'mintTime': 1705679481,
    'mintTx': 'ZJGoayaNDf2dLzknCjjaE9QjqxocA94pcegiF1oLsGZ841EMWBEc7TnDKLvCnE8cCVfkvoTNYCdMyhrWFFwPX6R',
    'mutableMetadata': True,
    'nonTransferable': None,
    'ownerAddress': None,
    'ownerBalance': None,
    'ownerPercentage': None,
    'preMarketHolder': [],
    'top10HolderBalance': 357579981.3372284,
    'top10HolderPercent': 0.6439307358062863,
    'top10UserBalance': 138709981.9366756,
    'top10UserPercent': 0.24978920911102176,
    'totalSupply': 555308143.3354646,
    'transferFeeData': None,
    'transferFeeEnable': None}
    '''

    # API endpoint for getting token security information
    url = f"{BASE_URL}/token_security?address={address}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    # Sending a GET request to the API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        security_data = response.json()['data']
        print_pretty_json(security_data)
    else:
        print("Failed to retrieve token security info:", response.status_code)

def token_creation_info(address):

    '''
    output sampel =

    Token Creation Info:
{   'decimals': 9,
    'owner': 'AGWdoU4j4MGJTkSor7ZSkNiF8oPe15754hsuLmwcEyzC',
    'slot': 242801308,
    'tokenAddress': '9dQi5nMznCAcgDPUMDPkRqG8bshMFnzCmcyzD8afjGJm',
    'txHash': 'ZJGoayaNDf2dLzknCjjaE9QjqxocA94pcegiF1oLsGZ841EMWBEc7TnDKLvCnE8cCVfkvoTNYCdMyhrWFFwPX6R'}
    '''
    # API endpoint for getting token creation information
    url = f"{BASE_URL}/token_creation_info?address={address}"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    # Sending a GET request to the API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        creation_data = response.json()['data']
        print_pretty_json(creation_data)
    else:
        print("Failed to retrieve token creation info:", response.status_code)

def market_buy(token: str, amount: float, slippage: int = SLIPPAGE) -> bool:
    """Execute a market buy order using Jupiter API"""
    try:
        # Initialize Jupiter client
        jupiter = JupiterClient()
        
        # Get wallet public key
        wallet_key = Keypair.from_base58_string(os.getenv("SOLANA_PRIVATE_KEY"))
        wallet_pubkey = str(wallet_key.pubkey())
        
        # Get quote for USDC to token swap
        quote = jupiter.get_quote(
            input_mint=USDC_ADDRESS,
            output_mint=token,
            amount=int(amount),
            slippage_bps=slippage
        )
        if not quote:
            return False
            
        # Execute swap
        tx = jupiter.execute_swap(quote, wallet_pubkey)
        if not tx:
            return False
            
        cprint(f"✅ Market buy executed: {amount} -> {token}", "green")
        return True
    except Exception as e:
        cprint(f"❌ Market buy failed: {str(e)}", "red")
        return False

def market_sell(token: str, amount: float, slippage: int = SLIPPAGE) -> bool:
    """Execute a market sell order using Jupiter API"""
    try:
        # Initialize Jupiter client
        jupiter = JupiterClient()
        
        # Get wallet public key
        wallet_key = Keypair.from_base58_string(os.getenv("SOLANA_PRIVATE_KEY"))
        wallet_pubkey = str(wallet_key.pubkey())
        
        # Get quote for token to USDC swap
        quote = jupiter.get_quote(
            input_mint=token,
            output_mint=USDC_ADDRESS,
            amount=int(amount),
            slippage_bps=slippage
        )
        if not quote:
            return False
            
        # Execute swap
        tx = jupiter.execute_swap(quote, wallet_pubkey)
        if not tx:
            return False
            
        cprint(f"✅ Market sell executed: {amount} {token} -> USDC", "green")
        return True
    except Exception as e:
        cprint(f"❌ Market sell failed: {str(e)}", "red")
        return False

def round_down(value: float, decimals: int) -> float:
    """Round down a float value to specified number of decimal places"""
    factor = 10 ** decimals
    return math.floor(value * factor) / factor

def get_time_range(days_back: int) -> tuple[int, int]:
    """Get time range with specified days lookback"""
    now = datetime.now()
    earlier = now - timedelta(days=days_back)
    time_to = int(now.timestamp())
    time_from = int(earlier.timestamp())
    return time_from, time_to

def get_data(address: str, days_back_4_data: int, timeframe: str) -> pd.DataFrame:
    """Get market data using Helius API"""
    try:
        client = HeliusClient()
        return client.get_token_data(address, days_back_4_data, timeframe)
    except Exception as e:
        cprint(f"❌ Error getting market data: {str(e)}", "red")
        return pd.DataFrame()

def fetch_wallet_holdings_og(wallet_address: str) -> pd.DataFrame:
    """Fetch token holdings for a wallet using Helius API"""
    df = pd.DataFrame(columns=['Mint Address', 'Amount', 'USD Value'])
    try:
        # Get wallet SOL balance
        helius_client = HeliusClient()
        sol_balance = helius_client.get_wallet_balance(wallet_address)
        if sol_balance > 0:
            df = pd.DataFrame([{
                'Mint Address': 'So11111111111111111111111111111111111111112',  # Native SOL mint
                'Amount': sol_balance,
                'USD Value': sol_balance * 100  # Approximate SOL price
            }])
            
        # Get token accounts
        response = requests.post(
            f"{helius_client.base_url}",
            headers=helius_client.headers,
            json={
                "jsonrpc": "2.0",
                "id": "get-token-accounts",
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                    {"encoding": "jsonParsed"}
                ]
            }
        )
        response.raise_for_status()
        data = response.json()
        
        if "result" in data and "value" in data["result"]:
            accounts = data["result"]["value"]
            rows = []
            
            for account in accounts:
                if "data" in account["account"] and "parsed" in account["account"]["data"]:
                    token_info = account["account"]["data"]["parsed"]["info"]
                    mint = token_info.get("mint")
                    amount = float(token_info.get("tokenAmount", {}).get("uiAmount", 0))
                    
                    # Get token price
                    price = float(helius_client.get_token_price(mint) or 0)
                    usd_value = amount * price
                    
                    if usd_value > 0.05:  # Only include tokens worth more than $0.05
                        rows.append({
                            'Mint Address': mint,
                            'Amount': amount,
                            'USD Value': usd_value
                        })
            
            if rows:
                df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                cprint(f'Total USD balance: ${df["USD Value"].sum():.2f}', 'white', 'on_green')
            
        return df
    except Exception as e:
        cprint(f"Error fetching wallet holdings: {str(e)}", 'white', 'on_red')
        return df











    return df

def fetch_wallet_token_single(address, token_mint_address):

    df = fetch_wallet_holdings_og(address)

    # filter by token mint address
    df = df[df['Mint Address'] == token_mint_address]

    return df


def token_price(address):
    """Get token price using Helius API"""
    try:
        client = HeliusClient()
        return client.get_token_price(address)
    except Exception as e:
        cprint(f"❌ Error getting token price: {str(e)}", "red")
        return None
    
# Example: price = token_price('token_address')


def get_position(token_mint_address):
    """
    Fetches the balance of a specific token given its mint address from a DataFrame.

    Parameters:
    - dataframe: A pandas DataFrame containing token balances with columns ['Mint Address', 'Amount'].
    - token_mint_address: The mint address of the token to find the balance for.

    Returns:
    - The balance of the specified token if found, otherwise a message indicating the token is not in the wallet.
    """
    dataframe = fetch_wallet_token_single(address, token_mint_address)

    #dataframe = pd.read_csv('data/token_per_addy.csv')

    print('-----------------')
    #print(dataframe)

    #print(dataframe)

    # Check if the DataFrame is empty
    if dataframe.empty:
        print("The DataFrame is empty. No positions to show.")
        return 0  # Indicating no balance found

    # Ensure 'Mint Address' column is treated as string for reliable comparison
    dataframe['Mint Address'] = dataframe['Mint Address'].astype(str)

    # Check if the token mint address exists in the DataFrame
    if dataframe['Mint Address'].isin([token_mint_address]).any():
        # Get the balance for the specified token
        balance = dataframe.loc[dataframe['Mint Address'] == token_mint_address, 'Amount'].iloc[0]
        #print(f"Balance for {token_mint_address[-4:]} token: {balance}")
        return balance
    else:
        # If the token mint address is not found in the DataFrame, return a message indicating so
        print("Token mint address not found in the wallet.")
        return 0  # Indicating no balance found


def get_decimals(token_mint_address):
    import requests
    import base64
    import json
    # Solana Mainnet RPC endpoint
    url = "https://api.mainnet-beta.solana.com/"
    headers = {"Content-Type": "application/json"}

    # Request payload to fetch account information
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            token_mint_address,
            {
                "encoding": "jsonParsed"
            }
        ]
    })

    # Make the request to Solana RPC
    response = requests.post(url, headers=headers, data=payload)
    response_json = response.json()

    # Parse the response to extract the number of decimals
    decimals = response_json['result']['value']['data']['parsed']['info']['decimals']
    #print(f"Decimals for {token_mint_address[-4:]} token: {decimals}")

    return decimals

def pnl_close(token_mint_address):

    ''' this will check to see if price is > sell 1, sell 2, sell 3 and sell accordingly '''

    print(f'checking pnl close to see if its time to exit for {token_mint_address[:4]}...')
    # check solana balance


    # if time is on the 5 minute do the balance check, if not grab from data/current_position.csv
    balance = get_position(token_mint_address)

    # save to data/current_position.csv w/ pandas

    # get current price of token
    price = token_price(token_mint_address)

    usd_value = float(balance) * float(price) if balance and price else 0.0

    tp = float(sell_at_multiple) * float(USDC_SIZE) if sell_at_multiple and USDC_SIZE else 0.0
    sl = ((1 + float(STOP_LOSS_PERCENTAGE)) * float(USDC_SIZE)) if STOP_LOSS_PERCENTAGE and USDC_SIZE else 0.0
    sell_size = balance
    decimals = 0
    decimals = get_decimals(token_mint_address)
    #print(f'for {token_mint_address[-4:]} decimals is {decimals}')

    sell_size = int(sell_size * 10 **decimals)

    #print(f'bal: {balance} price: {price} usdVal: {usd_value} TP: {tp} sell size: {sell_size} decimals: {decimals}')

    while usd_value > tp:


        cprint(f'for {token_mint_address[:4]} value is {usd_value} and tp is {tp} so closing...', 'white', 'on_green')
        try:

            market_sell(token_mint_address, sell_size, SLIPPAGE)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_green')
            time.sleep(2)
            market_sell(token_mint_address, sell_size, SLIPPAGE)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_green')
            time.sleep(2)
            market_sell(token_mint_address, sell_size, SLIPPAGE)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_green')
            time.sleep(15)

        except:
            cprint('order error.. trying again', 'white', 'on_red')
            time.sleep(2)

        balance = get_position(token_mint_address)
        price = token_price(token_mint_address)
        usd_value = balance * price
        tp = sell_at_multiple * USDC_SIZE
        sell_size = balance
        sell_size = int(sell_size * 10 **decimals)
        print(f'USD Value is {usd_value} | TP is {tp} ')


    else:
        #print(f'for {token_mint_address[-4:]} value is {usd_value} and tp is {tp} so not closing...')
        hi = 'hi'
        #time.sleep(10)

    # while usd_value < sl but bigger than .05

    if usd_value != 0:
        #print(f'for {token_mint_address[-4:]} value is {usd_value} and sl is {sl} so not closing...')

        while usd_value < sl and usd_value > 0:

            sell_size = balance
            sell_size = int(sell_size * 10 **decimals)

            cprint(f'for {token_mint_address[:4]} value is {usd_value} and sl is {sl} so closing as a loss...', 'white', 'on_blue')

            #print(f'for {token_mint_address[-4:]} value is {usd_value} and tp is {tp} so closing...')
            try:

                market_sell(token_mint_address, sell_size)
                cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
                time.sleep(1)
                market_sell(token_mint_address, sell_size)
                cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
                time.sleep(1)
                market_sell(token_mint_address, sell_size)
                cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
                time.sleep(15)

            except:
                cprint('order error.. trying again', 'white', 'on_red')
                # time.sleep(7)

            balance = get_position(token_mint_address)
            price = token_price(token_mint_address)
            usd_value = balance * price
            tp = sell_at_multiple * USDC_SIZE
            sl = ((1+stop_loss_percentage) * USDC_SIZE)
            sell_size = balance

            sell_size = int(sell_size * 10 **decimals)
            print(f'balance is {balance} and price is {price} and usd_value is {usd_value} and tp is {tp} and sell_size is {sell_size} decimals is {decimals}')

            # break the loop if usd_value is 0
            if usd_value == 0:
                print(f'successfully closed {token_mint_address[:4]} usd_value is {usd_value} so breaking loop AFTER putting it on my dont_overtrade.txt...')
                with open('dont_overtrade.txt', 'a') as file:
                    file.write(token_mint_address + '\n')
                break

        else:
            print(f'for {token_mint_address[:4]} value is {usd_value} and tp is {tp} so not closing...')
            #time.sleep(10)
    else:
        print(f'for {token_mint_address[:4]} value is {usd_value} and tp is {tp} so not closing...')

def chunk_kill(token_mint_address, max_usd_order_size, slippage):
    """Kill a position in chunks"""
    cprint(f"\n🔪 Lumix AI Agent initiating position exit...", "white", "on_cyan")
    
    try:
        # Get current position using address from config
        df = fetch_wallet_token_single(address, token_mint_address)
        if df.empty:
            cprint("❌ No position found to exit", "white", "on_red")
            return
            
        # Get current token amount and value
        token_amount = float(df['Amount'].iloc[0])
        current_usd_value = float(df['USD Value'].iloc[0])
        
        # Get token decimals
        decimals = get_decimals(token_mint_address)
        
        cprint(f"📊 Initial position: {token_amount:.2f} tokens (${current_usd_value:.2f})", "white", "on_cyan")
        
        while current_usd_value > 0.1:  # Keep going until position is essentially zero
            # Calculate chunk size based on current position
            chunk_size = token_amount / 3  # Split remaining into 3 chunks
            cprint(f"\n🔄 Splitting remaining position into chunks of {chunk_size:.2f} tokens", "white", "on_cyan")
            
            # Execute sell orders in chunks
            for i in range(3):
                try:
                    cprint(f"\n💫 Executing sell chunk {i+1}/3...", "white", "on_cyan")
                    sell_size = int(chunk_size * 10**decimals)
                    market_sell(token_mint_address, sell_size, slippage)
                    cprint(f"✅ Sell chunk {i+1}/3 complete", "white", "on_green")
                    time.sleep(2)  # Small delay between chunks
                except Exception as e:
                    cprint(f"❌ Error in sell chunk: {str(e)}", "white", "on_red")
            
            # Check remaining position
            time.sleep(5)  # Wait for blockchain to update
            df = fetch_wallet_token_single(address, token_mint_address)
            if df.empty:
                cprint("\n✨ Position successfully closed!", "white", "on_green")
                return
                
            # Update position size for next iteration
            token_amount = float(df['Amount'].iloc[0])
            current_usd_value = float(df['USD Value'].iloc[0])
            cprint(f"\n📊 Remaining position: {token_amount:.2f} tokens (${current_usd_value:.2f})", "white", "on_cyan")
            
            if current_usd_value > 0.1:
                cprint("🔄 Position still open - continuing to close...", "white", "on_cyan")
                time.sleep(2)
            
        cprint("\n✨ Position successfully closed!", "white", "on_green")
        
    except Exception as e:
        cprint(f"❌ Error during position exit: {str(e)}", "white", "on_red")

def sell_token(token_mint_address, amount, slippage):
    """Sell a token"""
    try:
        cprint(f"📉 Selling {amount:.2f} tokens...", "white", "on_cyan")
        # Your existing sell logic here
        print(f"just made an order {token_mint_address[:4]} selling {int(amount)} ...")
    except Exception as e:
        cprint(f"❌ Error selling token: {str(e)}", "white", "on_red")

def kill_switch(token_mint_address):

    ''' this function closes the position in full

    if the usd_size > 10k then it will chunk in 10k orders
    '''

    # if time is on the 5 minute do the balance check, if not grab from data/current_position.csv
    balance = get_position(token_mint_address)

    # get current price of token
    price = token_price(token_mint_address)
    price = float(price)

    usd_value = balance * price

    if usd_value < 10000:
        sell_size = balance
    else:
        sell_size = 10000/price

    tp = sell_at_multiple * USDC_SIZE

    # round to 2 decimals
    sell_size = round_down(sell_size, 2)
    decimals = 0
    decimals = get_decimals(token_mint_address)
    sell_size = int(sell_size * 10 **decimals)

    #print(f'bal: {balance} price: {price} usdVal: {usd_value} TP: {tp} sell size: {sell_size} decimals: {decimals}')

    while usd_value > 0:


# 100 selling 70% ...... selling 30 left
        #print(f'for {token_mint_address[-4:]} closing position cause exit all positions is set to {EXIT_ALL_POSITIONS} and value is {usd_value} and tp is {tp} so closing...')
        try:

            market_sell(token_mint_address, sell_size, SLIPPAGE)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
            time.sleep(1)
            market_sell(token_mint_address, sell_size, SLIPPAGE)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
            time.sleep(1)
            market_sell(token_mint_address, sell_size, SLIPPAGE)
            cprint(f'just made an order {token_mint_address[:4]} selling {sell_size} ...', 'white', 'on_blue')
            time.sleep(15)

        except:
            cprint('order error.. trying again', 'white', 'on_red')
            # time.sleep(7)

        balance = float(get_position(token_mint_address) or 0)
        price = float(token_price(token_mint_address) or 0)
        usd_value = balance * price
        tp = float(sell_at_multiple or 0) * float(USDC_SIZE or 0)

        if usd_value < 10000:
            sell_size = balance
        else:
            sell_size = 10000/price if price else 0

        # down downwards to 2 decimals
        sell_size = round_down(sell_size, 2)

        decimals = 0
        decimals = get_decimals(token_mint_address)
        #print(f'xxxxxxxxx for {token_mint_address[-4:]} decimals is {decimals}')
        sell_size = int(sell_size * 10 **decimals)
        print(f'balance is {balance} and usd_value is {usd_value} EXIT ALL POSITIONS TRUE and sell_size is {sell_size} decimals is {decimals}')


    else:
        print(f'for {token_mint_address[:4]} value is {usd_value} ')
        #time.sleep(10)

    print('closing position in full...')

def close_all_positions():

    # get all positions
    open_positions = fetch_wallet_holdings_og(WALLET_ADDRESS)

    # loop through all positions and close them getting the mint address from Mint Address column
    for index, row in open_positions.iterrows():
        token_mint_address = row['Mint Address']

        # Check if the current token mint address is the USDC contract address
        cprint(f'this is the token mint address {token_mint_address} this is don not trade list {dont_trade_list}', 'white', 'on_magenta')
        if token_mint_address in dont_trade_list:
            print(f'Skipping kill switch for USDC contract at {token_mint_address}')
            continue  # Skip the rest of the loop for this iteration

        print(f'Closing position for {token_mint_address}...')
        kill_switch(token_mint_address)

def delete_dont_overtrade_file():
    if os.path.exists('dont_overtrade.txt'):
        os.remove('dont_overtrade.txt')
        print('dont_overtrade.txt has been deleted')
    else:
        print('The file does not exist')

def supply_demand_zones(token_address, timeframe, limit):

    print('starting supply and demand zone calculations..')

    sd_df = pd.DataFrame()

    time_from, time_to = get_time_range()

    df = get_data(token_address, time_from, time_to, timeframe)

    # only keep the data for as many bars as limit says
    df = df[-limit:]
    #print(df)
    #time.sleep(100)

    # Calculate support and resistance, excluding the last two rows for the calculation
    if len(df) > 2:  # Check if DataFrame has more than 2 rows to avoid errors
        df['support'] = df[:-2]['Close'].min()
        df['resis'] = df[:-2]['Close'].max()
    else:  # If DataFrame has 2 or fewer rows, use the available 'close' prices for calculation
        df['support'] = df['Close'].min()
        df['resis'] = df['Close'].max()

    supp = df.iloc[-1]['support']
    resis = df.iloc[-1]['resis']
    #print(f'this is support for 1h {supp_1h} this is resis: {resis_1h}')

    df['supp_lo'] = df[:-2]['Low'].min()
    supp_lo = df.iloc[-1]['supp_lo']

    df['res_hi'] = df[:-2]['High'].max()
    res_hi = df.iloc[-1]['res_hi']

    #print(df)


    sd_df[f'dz'] = [supp_lo, supp]
    sd_df[f'sz'] = [res_hi, resis]

    print('Supply and demand zones calculated')
    #print(sd_df)

    return sd_df


def elegant_entry(symbol, buy_under):

    pos = float(get_position(symbol) or 0)
    price = float(token_price(symbol) or 0)
    pos_usd = pos * price
    size_needed = float(USDC_SIZE or 0) - pos_usd
    if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
    else: chunk_size = size_needed

    chunk_size = int(chunk_size * 10**6)
    chunk_size = str(chunk_size)

    print(f'chunk_size: {chunk_size}')

    if pos_usd > (.97 * usd_size):
        print('position filled')
        time.sleep(10)

    # add debug prints for next while
    print(f'position: {round(pos,2)} price: {round(price,8)} pos_usd: ${round(pos_usd,2)}')
    print(f'buy_under: {buy_under}')
    while pos_usd < (.97 * usd_size) and (price < buy_under):

        print(f'position: {round(pos,2)} price: {round(price,8)} pos_usd: ${round(pos_usd,2)}')

        try:

            for i in range(orders_per_open):
                market_buy(symbol, chunk_size, slippage)
                # Print order status
                cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size}', 'white', 'on_blue')
                time.sleep(1)

            time.sleep(tx_sleep)

            pos = get_position(symbol)
            price = token_price(symbol)
            pos_usd = pos * price
            size_needed = usd_size - pos_usd
            if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
            else: chunk_size = size_needed
            chunk_size = int(chunk_size * 10**6)
            chunk_size = str(chunk_size)

        except:

            try:
                cprint(f'trying again to make the order in 30 seconds.....', 'light_blue', 'on_light_magenta')
                time.sleep(30)
                for i in range(orders_per_open):
                    market_buy(symbol, chunk_size, slippage)
                    # Print order status
                    cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size}', 'white', 'on_blue')
                    time.sleep(1)

                time.sleep(tx_sleep)
                pos = get_position(symbol)
                price = token_price(symbol)
                pos_usd = pos * price
                size_needed = usd_size - pos_usd
                if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
                else: chunk_size = size_needed
                chunk_size = int(chunk_size * 10**6)
                chunk_size = str(chunk_size)


            except:
                cprint(f'Final Error in the buy, restart needed', 'white', 'on_red')
                time.sleep(10)
                break

        pos = get_position(symbol)
        price = token_price(symbol)
        pos_usd = pos * price
        size_needed = usd_size - pos_usd
        if size_needed > max_usd_order_size: chunk_size = max_usd_order_size
        else: chunk_size = size_needed
        chunk_size = int(chunk_size * 10**6)
        chunk_size = str(chunk_size)


# like the elegant entry but for breakout so its looking for price > BREAKOUT_PRICE
def breakout_entry(symbol, BREAKOUT_PRICE):
    """Entry function for breakout trading strategy"""
    pos = float(get_position(symbol) or 0)
    price = float(token_price(symbol) or 0)
    pos_usd = pos * price
    size_needed = float(USDC_SIZE or 0) - pos_usd
    if size_needed > max_usd_order_size: 
        chunk_size = max_usd_order_size
    else: 
        chunk_size = size_needed

    chunk_size = int(chunk_size * 10**6)
    chunk_size = str(chunk_size)

    print(f'chunk_size: {chunk_size}')

    if pos_usd > (.97 * float(USDC_SIZE or 0)):
        print('position filled')
        time.sleep(10)
        return

    print(f'position: {pos:.2f} price: {price:.8f} pos_usd: ${pos_usd:.2f}')
    print(f'breakoutpurce: {BREAKOUT_PRICE}')
    
    breakout_price = float(BREAKOUT_PRICE or 0)
    while pos_usd < (.97 * float(USDC_SIZE or 0)) and price > breakout_price:
        print(f'position: {pos:.2f} price: {price:.8f} pos_usd: ${pos_usd:.2f}')

        try:
            for i in range(orders_per_open):
                market_buy(symbol, chunk_size, SLIPPAGE)
                cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size}', 'white', 'on_blue')
                time.sleep(1)

            time.sleep(tx_sleep)

            pos = float(get_position(symbol) or 0)
            price = float(token_price(symbol) or 0)
            pos_usd = pos * price
            size_needed = float(USDC_SIZE or 0) - pos_usd
            if size_needed > max_usd_order_size: 
                chunk_size = max_usd_order_size
            else: 
                chunk_size = size_needed
            chunk_size = int(chunk_size * 10**6)
            chunk_size = str(chunk_size)

        except Exception as e:
            try:
                cprint(f'Retrying order in 30 seconds: {str(e)}', 'light_blue', 'on_light_magenta')
                time.sleep(30)
                for i in range(orders_per_open):
                    market_buy(symbol, chunk_size, SLIPPAGE)
                    cprint(f'chunk buy submitted of {symbol[:4]} sz: {chunk_size}', 'white', 'on_blue')
                    time.sleep(1)

                time.sleep(tx_sleep)
                pos = float(get_position(symbol) or 0)
                price = float(token_price(symbol) or 0)
                pos_usd = pos * price
                size_needed = float(USDC_SIZE or 0) - pos_usd
                if size_needed > max_usd_order_size: 
                    chunk_size = max_usd_order_size
                else: 
                    chunk_size = size_needed
                chunk_size = int(chunk_size * 10**6)
                chunk_size = str(chunk_size)

            except Exception as e:
                cprint(f'Final Error in the buy: {str(e)}', 'white', 'on_red')
                time.sleep(10)
                break

        pos = float(get_position(symbol) or 0)
        price = float(token_price(symbol) or 0)
        pos_usd = pos * price
        size_needed = float(USDC_SIZE or 0) - pos_usd
        if size_needed > max_usd_order_size: 
            chunk_size = max_usd_order_size
        else: 
            chunk_size = size_needed
        chunk_size = int(chunk_size * 10**6)
        chunk_size = str(chunk_size)



def ai_entry(symbol, amount):
    """AI agent entry function for Lumix trading system 🤖"""
    cprint("🤖 Lumix AI Trading Agent initiating position entry...", "white", "on_blue")
    
    # amount passed in is the target allocation (up to 30% of usd_size)
    target_size = amount  # This could be up to $3 (30% of $10)
    
    pos = get_position(symbol)
    price = token_price(symbol)
    pos_usd = pos * price
    
    cprint(f"🎯 Target allocation: ${target_size:.2f} USD (max 30% of ${usd_size})", "white", "on_blue")
    cprint(f"📊 Current position: ${pos_usd:.2f} USD", "white", "on_blue")
    
    # Check if we're already at or above target
    if pos_usd >= (target_size * 0.97):
        cprint("✋ Position already at or above target size!", "white", "on_blue")
        return
        
    # Calculate how much more we need to buy
    size_needed = target_size - pos_usd
    if size_needed <= 0:
        cprint("🛑 No additional size needed", "white", "on_blue")
        return
        
    # For order execution, we'll chunk into max_usd_order_size pieces
    if size_needed > max_usd_order_size: 
        chunk_size = max_usd_order_size
    else: 
        chunk_size = size_needed

    chunk_size = int(chunk_size * 10**6)
    chunk_size = str(chunk_size)
    
    cprint(f"💫 Entry chunk size: {chunk_size} (chunking ${size_needed:.2f} into ${max_usd_order_size:.2f} orders)", "white", "on_blue")

    while pos_usd < (target_size * 0.97):
        cprint(f"🤖 AI Agent executing entry for {symbol[:8]}...", "white", "on_blue")
        print(f"Position: {round(pos,2)} | Price: {round(price,8)} | USD Value: ${round(pos_usd,2)}")

        try:
            for i in range(orders_per_open):
                market_buy(symbol, chunk_size, slippage)
                cprint(f"🚀 AI Agent placed order {i+1}/{orders_per_open} for {symbol[:8]}", "white", "on_blue")
                time.sleep(1)

            time.sleep(tx_sleep)
            
            # Update position info
            pos = get_position(symbol)
            price = token_price(symbol)
            pos_usd = pos * price
            
            # Break if we're at or above target
            if pos_usd >= (target_size * 0.97):
                break
                
            # Recalculate needed size
            size_needed = target_size - pos_usd
            if size_needed <= 0:
                break
                
            # Determine next chunk size
            if size_needed > max_usd_order_size: 
                chunk_size = max_usd_order_size
            else: 
                chunk_size = size_needed
            chunk_size = int(chunk_size * 10**6)
            chunk_size = str(chunk_size)

        except Exception as e:
            try:
                cprint("🔄 AI Agent retrying order in 30 seconds...", "white", "on_blue")
                time.sleep(30)
                for i in range(orders_per_open):
                    market_buy(symbol, chunk_size, slippage)
                    cprint(f"🚀 AI Agent retry order {i+1}/{orders_per_open} for {symbol[:8]}", "white", "on_blue")
                    time.sleep(1)

                time.sleep(tx_sleep)
                pos = get_position(symbol)
                price = token_price(symbol)
                pos_usd = pos * price
                
                if pos_usd >= (target_size * 0.97):
                    break
                    
                size_needed = target_size - pos_usd
                if size_needed <= 0:
                    break
                    
                if size_needed > max_usd_order_size: 
                    chunk_size = max_usd_order_size
                else: 
                    chunk_size = size_needed
                chunk_size = int(chunk_size * 10**6)
                chunk_size = str(chunk_size)

            except:
                cprint("❌ AI Agent encountered critical error, manual intervention needed", "white", "on_red")
                return

    cprint("✨ AI Agent completed position entry", "white", "on_blue")

def get_token_balance_usd(token_mint_address):
    """Get the USD value of a token position"""
    try:
        # Get the position data using existing function
        df = fetch_wallet_token_single(WALLET_ADDRESS, token_mint_address)
        
        if df.empty:
            print(f"🔍 No position found for {token_mint_address[:8]}")
            return 0.0
            
        # Get the USD Value from the dataframe
        usd_value = df['USD Value'].iloc[0]
        return float(usd_value)
        
    except Exception as e:
        print(f"❌ Error getting token balance: {str(e)}")
        return 0.0
