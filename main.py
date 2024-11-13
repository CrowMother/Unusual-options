from Modules import polygon
from Modules import yfinance
from Modules import sqlStuff
from Modules import schwab
from Modules import webhook
import time


def main():

    #create sql database and connection to it
    db = sqlStuff.sqlControl()

    #get the list of tickers at beginning of day
    tickers = None

    if db.tableCreated == True:
        #get the list of tickers
        tickers = yfinance.get_symbols()
        #filter the tickers
        tickers = yfinance.filter_symbols_by_parameters(tickers)
        
        #get the option chain data for each ticker and add it to the database
        for ticker in tickers:
            option_chain_data = schwab.get_option_chain_data(ticker)
            
            option_date = schwab.pull_data(option_chain_data, db)

    #create a loop that runs the check for new data
    while True:
        #iterate through the db and compare the data
        large_trades_total = []
        highest_id = db.get_max_id()
        for id in range(1, highest_id):
            try:
                print(id)
                #get the symbol from the database
                symbol = db.get_symbol(id)
                #replace empty spaces and prepend O:
                symbol = f"O:{symbol.replace(" ", "")}"
                
                #get the open interest from the database
                openInterest = db.get_data(id, "openInterst")
                
                large_trades = polygon.print_trades(symbol, openInterest)

                if large_trades:
                    for large_trade in large_trades:
                        large_trade['symbol'] = symbol
                        webhook.webhookout(large_trade)
                        db.set_sent(id)

            except Exception as e:
                print(f"Error with {symbol}: {e}")
                print(large_trades_total)
        
        if large_trades_total:
            print("Large trades found for the following tickers:")
            print(large_trades_total)








if __name__ == "__main__":
    main()