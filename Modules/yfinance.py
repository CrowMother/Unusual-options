import yfinance as yf
import pandas as pd
from Modules import universal
from Modules import secretkeys
from Modules import sqlStuff
from yahoo_fin import stock_info as si


#modify in the future to get passed indexes
def get_symbols_from_index(indexes, extra_stocks = None):
        all_tickers = []
        dow_tickers = si.tickers_dow()
        nasdaq_tickers = si.tickers_nasdaq()
        all_tickers = dow_tickers + nasdaq_tickers
        # all_tickers = []
        
        #get the tickers from sp500
        #get the tickers from dow
        #get rid of repeats by making symbols a dictionary
        symbols = {ticker: ticker for ticker in all_tickers}
        
        if extra_stocks != None:
            for stock in extra_stocks:
                symbols[stock] = stock
        #make it aphabetical
        symbols = dict(sorted(symbols.items()))
        


        return symbols
    
def filter_symbols_by_parameters(symbols, db, min_market_cap=1e9, min_avg_volume=400000, ycon = universal.connection_retry()):
    length = len(symbols)
    i = 0
    
    for ticker in symbols:
        
        print(f"Processing {ticker} ({i}/{length})...")
        if db.get_unique_stock(ticker) != None:
            print(f"{ticker} already exists in the database. Skipping...")
            continue
        ticker = filter(ticker, min_market_cap, min_avg_volume, ycon)
        if ticker:
            db.add_unique_stock(ticker)
        i += 1

    return symbols


        





def filter(ticker, min_market_cap, min_avg_volume, ycon):
     
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        

        # Extract market cap and average daily volume
        market_cap = info.get('marketCap', 0)
        avg_volume = info.get('averageVolume', 0)

        # Check if market cap is over $1 billion and average volume over 200k
        if market_cap > min_market_cap and avg_volume > min_avg_volume:
            
            ycon.reset()
            return ticker
            
    except Exception as e:
        print(f"\nError processing {ticker}: {e}. Retrying after a pause of {ycon.get_sleep_time()} seconds...")
        if ycon.retry():
            return filter(ticker, min_market_cap, min_avg_volume, ycon)
        else:
            return