import ez_tor
import pandas as pd
import datetime

market_data_url = 'https://coinmarketcap.com/all/views/all/'
        
def get_raw_crypto_text():
    return ez_tor.get_text(market_data_url)

def get_crypto_data_table():
    return pd.read_html(get_raw_crypto_text(), header = 0)[2]

def get(viola):
    return float(''.join([i for i in viola if i.isdigit() or i == '.']))

def get_crypto_data():
    timestamp = datetime.datetime.now()
    df = get_crypto_data_table()
    n = len(df.index)
    data = [(df.at[i, 'Name'], get(df.at[i, 'Price'])) for i in range(n)]
    return timestamp, data
            