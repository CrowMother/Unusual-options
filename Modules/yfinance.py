import yfinance as yf
import pandas as pd
from Modules import universal
from Modules import secretkeys


def get_symbols():
    """
    Returns a dictionary of stock symbols, with the key being the ticker and
    the value being the ticker. The dictionary is sorted alphabetically.

    Returns:
        dict: A dictionary of stock symbols
    """
    dow_tickers = si.tickers_dow()
    nasdaq_tickers = si.tickers_nasdaq()

    #get rid of repeats by making symbols a dictionary
    all_tickers = set( dow_tickers + nasdaq_tickers)
    symbols = {ticker: ticker for ticker in all_tickers}
    #make it aphabetical
    symbols = dict(sorted(symbols.items()))

    return symbols
    
def filter_symbols_by_parameters(symbols):
    filtered_symbols = {}
    length = len(symbols)
    i = 0

    for ticker in symbols:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            i += 1

            # Extract market cap and average daily volume
            market_cap = info.get('marketCap', 0)
            avg_volume = info.get('averageVolume', 0)

            # Check if market cap is over $1 billion and average volume over 200k
            if market_cap > 1e9 and avg_volume > 200000:
                filtered_symbols[ticker] = {
                    'Market Cap': market_cap,
                    'Average Volume': avg_volume
                }
                PercentComplete((i / length) * 100, ticker)
            else:
                PercentComplete((i / length) * 100)
        
        except Exception as e:
            print(f"\nError processing {ticker}: {e}")

    return filtered_symbols

def get_option_chain_data(client, symbol):
    response = client.option_chains(symbol)
    if response.status_code == 200:
        # Parse the JSON content
        orders = response.json()
        return orders
    else:
        return None