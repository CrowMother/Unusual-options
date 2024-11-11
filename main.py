import schwabdev
from yahoo_fin import stock_info as si
import yfinance as yf
import pandas as pd
import sys
import sqlite3
from datetime import datetime, timedelta
import threading

from Modules import secretkeys

client = schwabdev.Client(secretkeys.get_app_key(), secretkeys.get_secret())


def main():

    #load filtered symbols into the database
    symbols = get_symbols()
    for symbol in symbols:
        #get the volume another way, need to be specific to each contract
        market_cap, avg_volume = filter_symbols_by_parameters(symbol)
        if market_cap and avg_volume:
            #pull data from schwabdev
            orders = get_option_chain_data(client, symbol)
            #get the date of the option
            for date in orders['callExpDateMap'].values():
                #get the options of that date
                for option in date.values():
                    values = option[0]
                    put_call = values['putCall']
                    open_interest = values['openInterest']
                    strike_price = values['strikePrice']

                    expiration_date = values['expirationDate']
                    expiration_date = convert_expiration_date(expiration_date)

                    avg_contract_volume = get_daily_average_volume(symbol, expiration_date, strike_price, put_call)

                    if open_interest > avg_contract_volume:
                        data = f"Symbol: {symbol}, Open Interest: {open_interest}, Strike Price: {strike_price}, Expiration Date: {expiration_date}"
                        send_webhook(data)
                    else:
                        print(f"symbol: {symbol}, open interest: {open_interest}, strike price: {strike_price}, expiration date: {expiration_date} volume too low: {avg_contract_volume}")
                        #send to webhook


def convert_expiration_date(expiration_date):
    """
    Convert expiration date from '2024-11-15T21:00:00.000+00:00' format to 'YYYY-MM-DD'.
    
    Parameters:
    expiration_date (str): The expiration date string in ISO 8601 format.

    Returns:
    str: The expiration date in 'YYYY-MM-DD' format.
    """
    dt = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d')

def get_daily_average_volume(symbol, expiration_date, strike_price, option_type='CALL', days=30):
    """
    Retrieve the daily average trading volume for a specific option contract over the past 'days'.

    Parameters:
    symbol (str): The stock ticker symbol (e.g., 'AAPL').
    expiration_date (str): The expiration date of the option in ISO 8601 format.
    strike_price (float): The strike price of the option.
    option_type (str): The type of option, either 'CALL' or 'PUT'. Default is 'CALL'.
    days (int): The number of days to calculate the average volume. Default is 30.

    Returns:
    float or str: The daily average trading volume of the specified contract or a message if not found.
    """
    # Convert the expiration date to 'YYYY-MM-DD' format
    formatted_expiration_date = convert_expiration_date(expiration_date)

    ticker = yf.Ticker(symbol)
    if formatted_expiration_date not in ticker.options:
        return f"Expiration date {formatted_expiration_date} not found for {symbol}."

    option_chain = ticker.option_chain(formatted_expiration_date)
    
    if option_type == 'CALL':
        options = option_chain.calls
    elif option_type == 'PUT':
        options = option_chain.puts
    else:
        return "Invalid option type. Use 'CALL' or 'PUT'."

    specific_option = options[options['strike'] == strike_price]

    if not specific_option.empty:
        historical_data = specific_option['volume'].iloc[0]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Pull historical option volume data if available (adjust as needed for API/library capabilities)
        # For example, you might need to use an external data source for this part.
        
        # Example placeholder for calculating average:
        average_volume = historical_data.mean()
        
        return average_volume
    else:
        return "Specific contract not found."


def send_webhook(data):
    print(f"sent webhook: {data}")

    
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
    
def filter_symbols_by_parameters(ticker, min_market_cap=1e9, min_avg_volume=200000):
    
    try:

        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract market cap and average daily volume
        market_cap = info.get('marketCap', 0)
        avg_volume = info.get('averageVolume', 0)

        # Check if market cap is over $1 billion and average volume over 200k
        if market_cap > min_market_cap and avg_volume > min_avg_volume:
            return market_cap, avg_volume
        else:
            return None, None
    
    except Exception as e:
        print(f"\nError processing {ticker}: {e}")


def get_option_chain_data(client, symbol):
    response = client.option_chains(symbol)
    if response.status_code == 200:
        # Parse the JSON content
        orders = response.json()
        return orders
    else:
        return None




main()