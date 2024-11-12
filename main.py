from Modules import polygon
from Modules import yfinance
from Modules import sqlStuff


def main():

    #create sql database and connection to it
    db = sqlStuff.sqlControl()

    #get the list of tickers at beginning of day
    
    #get the list of tickers
    tickers = yfinance.get_symbols()
    #filter the tickers
    tickers = yfinance.filter_symbols_by_parameters(tickers)
    
    #get the option chain data for each ticker and add it to the database





if __name__ == "__main__":
    main()