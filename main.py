from Modules import polygon
from Modules import yfinance
from Modules import sqlStuff
from Modules import schwab
from Modules import webhook
from Modules import universal
from Modules import secretkeys
import time


def main():

#set up variables for the program
    #get the indexes
    indexes = secretkeys.load_secret("INDEXES")
    extra_stocks = secretkeys.load_secret("EXTRA_STOCKS")
    #create sql database and connection to it
    db = sqlStuff.sqlControlMainTable()

    timeOutSystem = universal.connection_retry()
    #get the list of tickers at beginning of day
    tickers = None



    if db.tableCreated == True:

        extra_stocks = extra_stocks.split(",")
        #remove empty spaces
        extra_stocks = [stock.strip() for stock in extra_stocks]


        #get the list of tickers
        tickers = yfinance.get_symbols_from_index(indexes, extra_stocks)

        #filter the tickers
        #tickers = yfinance.filter_symbols_by_parameters(tickers, db)


        tickers = db.get_all_unique_stocks()
        #get the option chain data for each ticker and add it to the database
        for ticker in tickers:
            try:
                option_chain_data = schwab.get_option_chain_data(ticker)
                
                option_date = schwab.pullStore_data(option_chain_data, db)

            except Exception as e:
                print(f"Failed to get option chain data for {ticker}: {e}")
                continue

    #create a loop that runs the check for new data
    while True:
        #iterate through the db and compare the data
        large_trades_total = []
        highest_id = db.get_max_id()
        for id in range(1, highest_id):
            try:
                print(id)
                #get the symbol from the database
                plain_symbol = db.get_symbol(id)
                #replace empty spaces and prepend O:
                symbol = f"O:{plain_symbol.replace(" ", "")}"
                plain_symbol = plain_symbol.split(" ")[0]
                
                #get the open interest from the database
                openInterest = db.get_data(id, "openInterst")
                
                large_trades = polygon.get_large_trades(symbol, openInterest, timeOutSystem)

                if large_trades:
                    for large_trade in large_trades:
                        large_trade['symbol'] = symbol
                        large_trade['plain_symbol'] = plain_symbol
                        large_trade['expirationDate'] = db.get_data(id, "expirationDate")
                        large_trade['openInterest'] = db.get_data(id, "openInterst")
                        large_trade['callPut'] = db.get_data(id, "callPut")
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