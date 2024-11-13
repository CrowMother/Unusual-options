import schwabdev
import datetime
from Modules import secretkeys
from Modules import sqlStuff



client = schwabdev.Client(secretkeys.load_secret("SCHWAB_APP_KEY"), secretkeys.load_secret("SCHWAB_APP_SECRET"))

def get_option_chain_data(symbol):
    response = client.option_chains(symbol)
    if response.status_code == 200:
        # Parse the JSON content
        orders = response.json()
        return orders
    else:
        return None
    


def pull_data(option_chain_data, db):
    # Get the date and time for the current day
    callExpiration = option_chain_data['callExpDateMap']
    putExpiration = option_chain_data['putExpDateMap']
    pull_sub_data(callExpiration,db)



def pull_sub_data(expirations, db) :
    for expiration in expirations.items():
        strikes = expiration[1]
        for strike in strikes.items():
            strike_price = strike[0]
            subData = strike[1][0]

            #grab all the data needed for the database
            description = subData['description']
            expirationDate = subData['expirationDate']
            openInterest = subData['openInterest']
            lastPullTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            callPut = subData['putCall']
            symbol = subData['symbol']

            #add the data to the database
            db.add_stock(symbol, expirationDate, strike_price, openInterest, lastPullTime)



