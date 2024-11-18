from Modules import secretkeys
from Modules import universal
import time
import requests

def get_large_trades(option_ticker, openInterest, timeOutSystem, size_threshold_min = 50):


    # Replace with your Polygon.io API key
    if openInterest < size_threshold_min:
        return
    api_key = secretkeys.load_secret("API_KEY")

    #todays date in the format of YYYY-MM-DD
    today = time.strftime('%Y-%m-%d')

    #number of trades to look for
    num_trades = 50000

    # API endpoint
    url = f'https://api.polygon.io/v3/trades/{option_ticker}?timestamp={today}&order=desc&limit={num_trades}&sort=timestamp'

    # Headers for authorization
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    # Parameters (optional: you can modify or add parameters as needed)
    params = {
        'limit': 1000  # Adjust as necessary
    }

    # Make the API request
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        trades = response.json().get('results', [])
        if not trades:
            print("No trades found for the specified option.")
        else:
            # Define your size threshold (number of contracts in a trade)

            # Filter trades by size
            large_trades = [trade for trade in trades if trade['size'] > openInterest]

            if large_trades:
                return large_trades
            else:
                print("No trades exceeded the size threshold.")
    elif response.status_code == 443:
        print(f"Rate limit exceeded: Waiting for {timeOutSystem.get_sleep_time()} seconds.")
        timeOutSystem.retry()
        return get_large_trades(option_ticker, timeOutSystem, openInterest, size_threshold_min)
    elif response.status_code == 403:
        print("Access denied: Your API key does not have the required permissions to access this data.")
    elif response.status_code == 401:
        print("Unauthorized: Please check if your API key is correct and valid.")
    else:
        print(f"Error: {response.status_code} - {response.text}")
