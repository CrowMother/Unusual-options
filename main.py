import schwabdev
from yahoo_fin import stock_info as si
import yfinance as yf
import pandas as pd
import sys
import sqlite3

from Modules import secretkeys

client = schwabdev.Client(secretkeys.get_app_key(), secretkeys.get_secret())


def main():
    print("hello world")

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('filtered_symbols.db')
    cursor = conn.cursor()

    # Create a table for storing the filtered symbols
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symbols (
            ticker TEXT PRIMARY KEY,
            market_cap REAL,
            average_volume INTEGER,
            open_interest REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    #figure out an interval to run this code on

    # Get major indices tickers and filter them
    # symbols = get_symbols()
    # filtered_symbols = filter_symbols_by_parameters(symbols)

    # # Insert filtered symbols into the database
    # for symbol, data in filtered_symbols.items():
    #     cursor.execute('''
    #         INSERT OR REPLACE INTO symbols (ticker, market_cap, average_volume)
    #         VALUES (?, ?, ?)
    #     ''', (symbol, data['Market Cap'], data['Average Volume']))
    
    # conn.commit()
    # conn.close()


    #get each symbol from the database
    cursor.execute('SELECT ticker FROM symbols')
    symbols = [row[0] for row in cursor.fetchall()]

    alerts = []

    # Loop through each symbol and get the option chain data
    for symbol in symbols:
        print(symbol)
        #get the average volume for the symbol from the database
        cursor.execute('SELECT average_volume FROM symbols WHERE ticker = ?', (symbol,))
        average_volume = cursor.fetchone()[0]
        option_chain_data = get_option_chain_data(client, symbol)
        #get the callexpDataMap
        callexpDataMap = option_chain_data['callExpDateMap']
        #get each day within the callexpDataMap
        i = 0
        for day in callexpDataMap:
            #get each option within the day
            expData = callexpDataMap[day]
            for option in expData:
                #print the option data
                strikeData = expData[option]
                zeroData = strikeData[0]
                openInterest = zeroData['openInterest']
                print(openInterest)
                #check if openInterest is greater than the value in the openInterest column
                if openInterest > average_volume:
                    print(f"Symbol: {symbol}, Open Interest: {openInterest}, Average Volume: {average_volume}")
                    alerts.append(f"Symbol: {symbol}, Open Interest: {openInterest}, Average Volume: {average_volume}, Date:{day}, option: {option}")

                    
    
def current_symbol(symbol, percentage, extra=None):
    progress_str = f"\rProgress: {percentage:.2f}% - working on {symbol}"
    
    # Print the string without adding a new line
    sys.stdout.write(progress_str)
    sys.stdout.flush()

def PercentComplete(percentage, symbol=None):
    # Format the percentage and symbol as a string with a '%' symbol
    if symbol:
        progress_str = f"\rProgress: {percentage:.2f}% - Added {symbol}"
    else:
        progress_str = f"\rProgress: {percentage:.2f}%"
    
    # Print the string without adding a new line
    sys.stdout.write(progress_str)
    sys.stdout.flush()

def get_symbols():
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

main()