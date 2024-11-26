from Modules import polygon
from Modules import yfinance
from Modules import sqlStuff
from Modules import schwab
from Modules import webhook
from Modules import universal
from Modules import secretkeys
import time
import yfinance as yf


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



    # if db.tableCreated == True:

    #     extra_stocks = extra_stocks.split(",")
    #     #remove empty spaces
    #     extra_stocks = [stock.strip() for stock in extra_stocks]


    #     #get the list of tickers
    #     tickers = yfinance.get_symbols_from_index(indexes, extra_stocks)

    #     #filter the tickers
    #     tickers = yfinance.filter_symbols_by_parameters(tickers, db)


    #     tickers = db.get_all_unique_stocks()
    #     #get the option chain data for each ticker and add it to the database
    #     for ticker in tickers:
    #         try:
                


    #             option_chain_data = schwab.get_option_chain_data(ticker)
                
    #             option_date = schwab.pullStore_data(option_chain_data, db)

    #         except Exception as e:
    #             print(f"Failed to get option chain data for {ticker}: {e}")
    #             continue

    #create a loop that runs the check for new data
    #while True:
        #iterate through the db and compare the data
    large_trades_total = []
    highest_id = int(db.get_max_id())
    previous_symbol = ""
    previous_call_put = ""

    highest_strike = 0
    minimum_strike = 0

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
            callPut = db.get_data(id, "callPut")



#create a function to make this more readable
            if previous_symbol != plain_symbol and previous_call_put != callPut:

                ticker = yf.Ticker(plain_symbol)
                current_price = ticker.info['currentPrice']

                #get the largest strike from the database with same expiration date
                exirationDate = db.get_data(id, "expirationDate")
                
                
                strikes = db.get_strikes(plain_symbol, exirationDate, callPut)
                #get the highest strike from the list of strikes
                strikeLength = len(strikes)

                #get the index closest to the current price
                index = 0
                for i in range(strikeLength):
                    if strikes[i] > current_price:
                        index = i
                        break
                delta_range = (strikeLength / 2) / 2 #getting half the range then half of that again to get the middle 50%

                highest_strike = setMaximumStrike(strikeLength, strikes, index, delta_range)
                minimum_strike = setMinimumStrike(strikeLength, strikes, index, delta_range)
                #check if the current strike of this id is inbetween the highest and lowest strike
                current_strike = float(db.get_data(id, "strike"))



            previous_symbol = plain_symbol
            previous_call_put = callPut
            if current_strike < minimum_strike or current_strike > highest_strike:
                print(f"Current strike {current_strike} is not inbetween {minimum_strike} and {highest_strike}")
                continue

            large_trades = polygon.get_large_trades(symbol, openInterest, timeOutSystem)

            if large_trades:
                for large_trade in large_trades:
                    large_trade['symbol'] = symbol
                    large_trade['plain_symbol'] = plain_symbol
                    large_trade['expirationDate'] = db.get_data(id, "expirationDate")
                    large_trade['openInterest'] = db.get_data(id, "openInterst")
                    large_trade['callPut'] = db.get_data(id, "callPut")
                    large_trade['strike'] = db.get_data(id, "strike")
                    price = large_trade['price']
                    size = large_trade['size']
                    total_price = price * (size * 100)
                    
                    if total_price < 10000:
                        continue #skip this trade if its less than $10k

                    webhook.webhookout(large_trade)
                    db.set_sent(id)
                    print(f"Data:\n")


        except Exception as e:
            print(f"Error with {symbol}: {e}")
            print(large_trades_total)
    
    if large_trades_total:
        print("Large trades found for the following tickers:")
        print(large_trades_total)



def setMaximumStrike(strikeLength, strikes, index, delta_range):
    #check if the max or min strikes are within the range
    if index + int(delta_range) >= strikeLength:
        return max(strikes) #return the highest strikes
    return strikes[index + int(delta_range)]

def setMinimumStrike(strikeLength, strikes, index, delta_range):
    if index - int(delta_range) < 0:
        return min(strikes)
    return strikes[index - int(delta_range)]


if __name__ == "__main__":
    main()