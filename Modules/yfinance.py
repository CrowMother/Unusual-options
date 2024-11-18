import yfinance as yf
import pandas as pd
from Modules import universal
from Modules import secretkeys
from yahoo_fin import stock_info as si


#modify in the future to get passed indexes
def get_symbols_from_index(indexes, extra_stocks = None):
    if indexes != None:
        all_tickers = []
        for index in indexes:
            tickers = si.tickers_on_index(index)
            all_tickers = all_tickers + tickers
        #get rid of repeats by making symbols a dictionary
        
        symbols = {ticker: ticker for ticker in all_tickers}
        
        if extra_stocks != None:
            for stock in extra_stocks:
                symbols[stock] = stock
        #make it aphabetical
        symbols = dict(sorted(symbols.items()))
        


        return symbols
    
def filter_symbols_by_parameters(symbols, min_market_cap=1e9, min_avg_volume=200000, ycon = universal.connection_retry()):
    filtered_symbols = []
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
            if market_cap > min_market_cap and avg_volume > min_avg_volume:
                filtered_symbols.append(ticker)
                print(f"Added {ticker} to filtered_symbols ({i}/{length})")
                ycon.reset()

        except Exception as e:
            print(f"\nError processing {ticker}: {e}. Retrying after a pause of {ycon.get_sleep_time()} seconds...")
            ycon.retry()
            return filter_symbols_by_parameters(ticker, min_market_cap, min_avg_volume, ycon)

    return filtered_symbols

