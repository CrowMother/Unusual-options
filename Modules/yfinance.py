import yfinance as yf
import pandas as pd
from Modules import universal
from Modules import secretkeys
from yahoo_fin import stock_info as si


#modify in the future to get passed indexes
def get_symbols():
    dow_tickers = si.tickers_dow()
    nasdaq_tickers = si.tickers_nasdaq()

    #get rid of repeats by making symbols a dictionary
    all_tickers = set( dow_tickers + nasdaq_tickers)
    symbols = {ticker: ticker for ticker in all_tickers}
    #make it aphabetical
    symbols = dict(sorted(symbols.items()))

    return symbols
    
def filter_symbols_by_parameters(symbols, min_market_cap=1e9, min_avg_volume=200000):
    filtered_symbols = []
    length = len(symbols)
    i = 0

    for ticker in symbols:
        try:
            ycon = universal.connection_retry()
            stock = yf.Ticker(ticker)
            info = stock.info
            i += 1

            # Extract market cap and average daily volume
            market_cap = info.get('marketCap', 0)
            avg_volume = info.get('averageVolume', 0)

            # Check if market cap is over $1 billion and average volume over 200k
            if market_cap > min_market_cap and avg_volume > min_avg_volume:
                filtered_symbols.append(ticker)
                print(f"Added {ticker} to filtered_symbols ({i}/{length})")

        except Exception as e:
            print(f"\nError processing {ticker}: {e}. Retrying after a pause of {ycon.sleep_time} seconds...")
            ycon.retry()
            continue  # Retry the same ticker

    return filtered_symbols

