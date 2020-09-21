from cmc_api import process_cur_data
import os
import pandas as pd
import json

#data about where to save everything
working_dir = 'C:/Users/willi/OneDrive/Documents/python_scripts/checkz/data'
working_file = 'cur'
dict_file = 'dict'

path = working_dir + '/' + working_file + '.xlsx' 
dict_path = working_dir + '/' + dict_file + '.txt'

def handle_dir_creation():
    '''
    simply makes the worlind directory if it does not exist
    '''
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
        
def get_cur_dataset():
    '''
    Get the current dataset from the api wrapper file, and return a sort of 
    representation with more redundancy and easier use
    snapshot = process_cur_

    Returns
    -------
    timestamp : string
        A string representing the timestamp at which the data was gathered
    order : list
        A list of the names of this coins in the order of the cmc ranking.
    names : dict
        a dictionary with keys names and values their cmc ids
    prices : dict
        a dictionary with the keys names and the values the prices
    '''
    snapshot = process_cur_data()
    timestamp = snapshot.timestamp
    order = [coin.name for coin in snapshot.crypto_data]
    names = dict([(coin.name, coin.cmc_id) for coin in snapshot.crypto_data])
    prices = dict([(coin.name, coin.price) for coin in snapshot.crypto_data])
    return timestamp, order, names, prices

def read_stored_data():
    '''
    Reads the data that's currently stored in the excel and json files.

    Returns
    -------
    dataframe
        pandas dataframe with each cryptocurrency and it's price over time
    dictionary
        a dictionary with crypto names and their cmc ids
    '''
    try:
        df = pd.read_excel(path, index_col = 0)
        names_dict = json.load(open(dict_path, 'r'))
        return df, names_dict
    except:
        #something screwed up
        return None, None
    
def update():
    '''
    This updates the stored data by pulling and adding to the data
    '''
    time, order, names, prices = get_cur_dataset() #new data
    df, names_dict = read_stored_data() #old data
    if df is None or names_dict is None:
        #there's nothing stored, set the result to just the new data
        names_dict = names
        df = pd.DataFrame({time : prices}, index = order)
    else:
        #combine the old and new data
        extras = set(df.index).difference(set(order))
        new_index = order + sorted(list(extras))
        names_dict = {**names_dict, **names}
        cur_dict = df.to_dict(orient = 'dict')
        cur_dict[time] = prices
        df = pd.DataFrame(cur_dict)
        df = df.sort_values(new_index, axis = 1)
    #makes sure that this doesn't end up taking up too much memory
    if len(df.T.columns) > 7 * 48:
        df = df.T.tail(7 * 48).T
    #write all the data to the save location
    df.to_excel(path)
    json.dump(names_dict, open(dict_path, 'w'), indent = 4)
 
if __name__ == '__main__':
    update()