from Modules import secretkeys
from Modules import universal
import requests


def print_trades():
    # Replace with your Polygon.io API key

    api_key = secretkeys.load_secret("API_KEY")

    # Option ticker symbol (e.g., 'O:SPY241115C00450000')
    option_ticker = 'O:SPY241115C00450000'

    # API endpoint
    url = f'https://api.polygon.io/v3/trades/{option_ticker}'

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
            # Define your size threshold
            size_threshold = 100  # Replace with your desired threshold

            # Filter trades by size
            large_trades = [trade for trade in trades if trade['size'] > size_threshold]

            if large_trades:
                for trade in large_trades:
                    print(trade)
            else:
                print("No trades exceeded the size threshold.")
    elif response.status_code == 403:
        print("Access denied: Your API key does not have the required permissions to access this data.")
    elif response.status_code == 401:
        print("Unauthorized: Please check if your API key is correct and valid.")
    else:
        print(f"Error: {response.status_code} - {response.text}")
