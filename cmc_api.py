from requests import Session
import json
from datetime import datetime as dt
from secret_info import cmc_api_key

#url for the api
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

#200 is the most currencies one can grab in a single api call
parameters = {
  'start':'1',
  'limit':'200',
  'convert':'USD'
}

#feeds the api with your api key
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': cmc_api_key,
}

#a class for a datum of a cryptocurrency name and price
class crypto_datum:
    def __init__(self, name, cmc_id, price):
        self.name = name
        self.cmc_id = cmc_id
        self.price = price

#a simple class that's a list of crypto data with a timestamp
class market_snapshot:
    def __init__(self, crypto_data, timestamp = None):
        self.crypto_data = crypto_data
        if not timestamp is None:
            self.timestamp = timestamp
        else: 
            self.timestamp = dt.now().strftime("%m/%d/%YT%H:%M:%S")

def get_cur_data():
    '''
    Request the current api call result and return it, if successful
    Returns
    -------
    data : json
        the result of calling the api for the current data
    '''
    session = Session()
    session.headers.update(headers) #enter api key
    try:
      response = session.get(url, params=parameters)
      data = json.loads(response.text)
      return data
    except:
      return None
  
def process_cur_data():
    '''
    Requests the current data, parses it, and returns it in parsed form

    Returns
    -------
    snapshot : market_snapshot
        Market snapshot of the current market data
    '''
    data_dict = get_cur_data() #get the raw data
    if data_dict is None:
        return None
    #this is how the json parses from the format of what's returned
    coins = data_dict['data']
    crypto_data = []
    for coin in coins:
        coin_id = coin['id']
        coin_name = coin['name'].lower()
        coin_val = coin['quote']['USD']['price']
        crypto_data.append(crypto_datum(coin_name, coin_id, coin_val))
    timestamp_raw = data_dict['status']['timestamp']
    timestamp = timestamp_raw[:timestamp_raw.index('.')]
    snapshot = market_snapshot(crypto_data, timestamp)
    return snapshot