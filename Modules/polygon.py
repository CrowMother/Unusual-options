from Modules import secretkeys
from Modules import universal
import time
import requests


def print_trades(option_ticker, size_threshold = 100, size_threshold_min = 50):


    timeoutValue = 15
    # Replace with your Polygon.io API key
    if size_threshold < size_threshold_min:
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
            large_trades = [trade for trade in trades if trade['size'] > size_threshold]

            if large_trades:
                return large_trades
            else:
                print("No trades exceeded the size threshold.")
    elif response.status_code == 443:
        timeoutValue += timeoutValue
        print("Rate limit exceeded: Waiting for 15 seconds.")
        time.sleep(timeoutValue)
        return print_trades(option_ticker, size_threshold, size_threshold_min)
    elif response.status_code == 403:
        print("Access denied: Your API key does not have the required permissions to access this data.")
    elif response.status_code == 401:
        print("Unauthorized: Please check if your API key is correct and valid.")
    else:
        print(f"Error: {response.status_code} - {response.text}")
