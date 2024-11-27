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
    


def pullStore_data(option_chain_data, db):
    # Get the date and time for the current day
    callExpiration = option_chain_data['callExpDateMap']
    putExpiration = option_chain_data['putExpDateMap']
    pull_sub_data(callExpiration,db)
    pull_sub_data(putExpiration,db)



def pull_sub_data(expirations, db) :
    #calculate range of the middle 50% of strike prices

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


            
            db.add_stock(symbol, expirationDate, strike_price, callPut, openInterest, lastPullTime)
            


def get_open_price(symbol):
    response = client.quote(symbol)
    if response.status_code == 200:
        # Parse the JSON content
        data = response.json()
        open_price = data[f'quote']['openPrice']
        return open_price
    else:
        return None


def get_highest_strike(symbol):
    response = client.quote(symbol)
    if response.status_code == 200:
        # Parse the JSON content
        data = response.json()
        highest_strike = data[f'quote']['highestStrike']
        return highest_strike
    else:
        return None