# libraries used in notebook function
from tqdm import tqdm

# To read url
import requests

# For Calculation and Data Manipulation
import numpy as np
import pandas as pd

# For `.pkl` file exportion folder creation
import os

# for datetime conversion
import datetime

# for data collection server buffer time
import time

# for data visualisation
import matplotlib.pyplot as plt
import seaborn as sns

# for approximate nearest neighbors
import hnswlib


# modified from https://pub.towardsai.net/knn-k-nearest-neighbors-is-dead-fc16507eb3e?sk=b964df6dccf263518b244d4264ba088d

def fit_hnsw_index(features, ef=300, M=100, save_index_file=False):
    # Convenience function to create HNSW graph
    # features : list of lists containing the embeddings
    # ef, M: parameters to tune the HNSW algorithm
    
    num_elements = len(features)
    labels_index = np.arange(num_elements)
    EMBEDDING_SIZE = len(features[0])
    
    # Declaring index
    # possible space options are l2, cosine or ip
    p = hnswlib.Index(space='l2', dim=EMBEDDING_SIZE)
    
    # Initing index - the maximum number of elements should be known
    p.init_index(max_elements=num_elements, ef_construction=ef, M=M)
    
    # Element insertion
    int_labels = p.add_items(features, labels_index)
    
    # Controlling the recall by setting ef
    # ef should always be > k
    p.set_ef(ef) 
    
    # If you want to save the graph to a file
    if save_index_file:
         p.save_index(save_index_file)
    
    return p

# modified from https://www.datacamp.com/community/tutorials/recommender-systems-python
# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(df, indices, title, cosine_sim):
    # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the games based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar titles
    sim_scores = sim_scores[1:11]

    # Get the titles indices
    name_indices = [i[0] for i in sim_scores]

    # create dataframe
    df_ret = pd.DataFrame(df['name'].iloc[name_indices])
    
    # attach score
    df_ret['cos_sim'] = pd.DataFrame(cosine_sim).iloc[name_indices,idx]
    
    # Return the top 10 most similar movies
    return df_ret



# function to plot multiple histogram
def multiple_histogram(row, col, xval, title, df, graph_suptitle, color, no_bins=15):
    """
    plot multiple histogram using seaborn on 1 data
    
    Parameters
    ----------
    Parameters to pass as part of function
    
    row : int
        number of rows
    col : int
        number of columns
    xval : list
        list of values to take as x-values for histogram plotting, in the form of row and column alternating. E.g. [r1,c1,r2,c2,...]
    title : list
        list of titles for histogram plotting, in the form of row and column alternating. E.g. [r1,c1,r2,c2,...]
    df : dataframe
        dataframe
    no_bins : int
        number of bins for histogram
    graph_suptitle : string
        overall title of all graphs
    color : list
        color of graph to be plot, in the form of row and column alternating. E.g. [r1,c1,r2,c2,...]
        
    Return
    ------
    value returned after calling the function
    
    None 
        None is being returned
    
    """
    
    # to have subplots with row and col and figsize = (16, 9)
    fig, axes = plt.subplots(row, col, figsize=(16,9))
    
    # define suptitle of graph
    fig.suptitle(graph_suptitle)
    
    # counter for graph plotting
    counter = 0
    
    # if is 1 row or 1 col
    if (row==1) or (col==1):
        # loop through the number of rows/cols
        for i in range(max(row, col)):
            # plot graph
            sns.histplot(ax=axes[i], x = xval[counter], data = df, bins=no_bins, kde=True, color = color[counter])
            # set title of graph
            axes[i].set_title(title[counter])
            # update counter
            counter +=1
    # for graphs with more than 1 row and 1 col
    else:
        # loop through row
        for r in range(row):
            # loop through column
            for c in range(col):
                sns.histplot(ax=axes[r,c], x = xval[counter], data = df, bins=no_bins, kde=True, color = color[counter])
                # set title of graph
                axes[r,c].set_title(title[counter])
                # update counter
                counter +=1
    
    # adjust the graph layout
    plt.tight_layout() 
    
    # show the graph
    plt.show();

# function to plot correlation graph
def plot_heatmap(df, title, color='YlGnBu'):
    """
    plot heat map of correlation of df using seaborn
    
    Parameters
    ----------
    Parameters to pass as part of num_col_null
    
    df : dataframe
        dataframe
    title : string
        title of graph
    color : string
        color of graph to be plot. Default value: 'YlGnBu'
        
    Return
    ------
    value returned after calling the function
    
    None 
        None is being returned
    
    """
    
    # create mask for heatmap
    df_mask = np.zeros_like(df.corr())
    df_mask[np.triu_indices_from(df_mask)] = True
    
    # plot heat map
    sns.heatmap(data=df.corr(), annot=True, linewidth = 0.3, mask = df_mask, cmap=color)
    plt.title(title)
    
    # adjust the graph layout
    plt.tight_layout() 
    
    # show the graph
    plt.show();

# function to unpack out list containing dictionaries or dictionaries
def unpack_cell(df, unpacked_col, new_col, key):
    """
    create new column within dataframe storing what is requested and return a collection of unique dictionaries
    
    Parameters
    ----------
    Parameters to pass as part of num_col_null
    
    df : dataframe
        dataframe containing column.
    unpacked_col : string
        column name in dataframe
    new_col : string
        column name in dataframe
    key : string
        'key' that is being unpacked from dictionary
        
    Return
    ------
    value returned after calling the function
    
    list_col : list
        list containing a collection of unique dictionaries that was unpacked
    
    """

    
    #============
    
    # store all possible dictionaries
    list_col = [] 
    
    # store list to attach to new_col
    cat_list = []
    
    # loop to extract dictionary
    for index, row in tqdm(df[unpacked_col].iteritems(), total=len(df)):
    #    if index > 55:
    #        break

        # create list to store value
        temp_list = []   
        
        # check if row is a list
        if type(row) == list:
            # check if is empty
            if row == []:
                cat_list.append(np.nan)
            else:
                # loop the list within the cell
                for i in range(len(row)):
                    # check if is existing identified value
                    if row[i] not in list_col:
                        # if is not in existing identified value, append
                        list_col.append(row[i])
                    temp_list.append(row[i].get(key, np.nan))
                cat_list.append(temp_list)
        else:
            if row not in list_col:
            # if is not in existing identified value, append
                list_col.append(row)
            cat_list.append(row.get(key, np.nan))
    
    # attach list to new_col in df
    df[new_col] = cat_list
    
    return list_col


# function to print null values
def num_col_null(df):
    """
    Return dataframe of column containing null values, along with the column and number of null values within the column and percentage
    
    Parameters
    ----------
    Parameters to pass as part of num_col_null
    
    df : dataframe
        dataframe that is being identified for null values. 
        
    Return
    ------
    value returned after calling the function
    
    temp_df : dataframe
        dataframe containing the null value details
    
    """
    
    #============
    
    # create varaible of sum 
    null_sum = df.isnull().sum()
    
    # create variable of columns with null values
    col_null_exist = df.columns[null_sum>0]
    
    # number of columns with null values
    print(f"Number of columns with null values: {len(col_null_exist)}\n")
    
    # empty list to store inputs
    list_col = []
    list_value = []
    list_percentage = []
    
    # columns : null value
    for index, value in enumerate(null_sum):
        if value > 0: 
            list_col.append(df.columns[index])
            list_value.append(value)
            list_percentage.append((value/len(df)))
            #print(f"Number of null values in {df.columns[index]}: {value}. Percentage: {(value/len(df)):.4f}")
    
    
    temp_df = pd.DataFrame(data = {"column": list_col, "number of null values": list_value, "percentage": list_percentage})
    
    return temp_df


# Generic Function to get requests from an API
def get_request(url, parameters=None):
    """
    Return json-formatted response of a get request using optional parameters
    
    Parameters
    ----------
    Parameters to pass as part of get_requests
    
    url : string
        url of API
    parameters : {'API_prarmeter': 'value'}
        parameters that the api accepts
        
    Return
    ------
    value returned after calling the function
    
    response.json : json_data
        json-formatted resposnse (dict-like)
    None
    
    """
   
    #===============
    
    # code run, to run `except` line if error
    try: 
        response = requests.get(url = url, params = parameters)
     
    # code to run SSLError if error prompt from `try` code
    except SSLError as s:
        print(f'SSL Error : {s}')
        
        # Waiting time of 5s
        # \r: carriage return, return print to start of curent line instead 
        for i in range(5, 0, -1):
            print('\rWaiting...  ({})')  # print countdown of waiting time
            time.sleep(1)     # wait for 1 second
        
        # check with user if want to retry:
        user_input = input("Do you want to retry?\nResponse (Y/N):")
        
        # if input is neither 'y' or 'n'
        if (user_input.lower() != 'y') & (user_input.lower() != 'n'):
            # inform that their input is not a valid option and reprompt user
            print('Invalid response received.')
            user_input = input("Do you want to retry?\nResponse (Y/N):")
        
        # if input is 'n'
        elif user_input.lower() == 'n': 
            # user indicated that they do not wad to retry
            print('User do not want to continue, loop stop.')
            return None
        else: 
            # to inform user about retrying to get request
            print('\rRetrying...' + ' '*8)    # inform user we are retrying to get the request
            
            # rerun function to get request
            return get_request(url, parameters)
    
    if response: 
        return response.json()
    else:
        # reponses is none means there is too many requests. Wait and try again
        print('No response, waiting 10 seconds...')
        time.sleep(10)
        # inform user function will retry
        print('Retrying...')
        return get_request(url, parameters)
    
    return None


# Function to save dataframe into pkl
def pkl_output(filename, df):
    """
    Creating a pkl file or overwriting existing pkl file
    
    Parameters
    ----------
    Parameters to pass as part of pkl_output
    
    filename : string
        folder/file path and name of file. E.g. '../data/name.pkl'
    df : Dataframe
        Dataframe that we want to save into a file path
        
    Return
    ------
    value returned after calling the function
    
    None
        A pkl file should be created in the folder location indicated by filename as specified
    
    """
    
    #===============
    
    # filename of output
    output_path = filename
    
    # create data folder if it does not exist in current folder,
    if not os.path.exists('../data'):
        os.makedirs('../data')
    
    # append file to pkl file
    pd.DataFrame(df).to_pickle(output_path)
    
    return None
    

# Function to get data
def get_game_data(start, stop, fn, app_list, pause = 2):
    """
    Function to get and store one batch of game data before returning to multiple batch process function
    
    Parameters
    ----------
    Parameters to pass as part of get_data
    
    start : integer
        index of starting value for app_list (overall)
    stop : integer
        index of stopping value for app_list (overall)
    fn : function
        Function used to scrap data
    pause : integer / float
        value of pause time in seconds for each scrapping. Default is 2 seconds.
    app_list : list
        list of applications
        
    Return
    ------
    value returned after calling the function
    
    game_data : dataframe
        dataframe containing the game data for app_list[start:stop]
    
    """
    
    #===============
    
    game_data = pd.DataFrame()
    
    # start printing on new line
    print()
    
    # iterate through each row of app_id within start and stop
    for index, row in app_list[start:stop].iterrows():
        # inform user current which index is being requested
        print(f'Current index: {index}', end='\r')
        
        appid = row['app_id']
        name = row['game_name']
        
        # retrieve game data for a row, handled by supllied function, and append to dataframe
        data = fn(appid, name)
        game_data = game_data.append(data, ignore_index=True)
        
        # prevent overloading api with requests
        time.sleep(pause)
    return game_data



# scrap data from steam
def steam_data_request(appid, name):
    """
    Function to get game data from steam
    
    Parameters
    ----------
    Parameters to pass as part of steam_data_request
    
    appid : integer
        application / game id
    name : string
        application / game name
        
    Return
    ------
    value returned after calling the function
    
    data : dictionary
        dictionary containing the game data for appid/name.
    
    """
    
    #===============
    
    # set the parameters to get request from steam
    steam_url = "http://store.steampowered.com/api/appdetails/"
    steam_parameters = {"appids": appid}
    
    # request the game details using API
    steam_json_data = get_request(steam_url, parameters=steam_parameters)
    steam_json_game_data = steam_json_data[str(appid)]
    
    # value to return depending of request success
    if steam_json_game_data['success']:
        data = steam_json_game_data['data']
    else:
        data = {'name':name, 'steam_appid': appid}
    
    return data



# scrap data from steamspy
def steamspy_data_request(appid, name):
    """
    Function to get game data from steamspy
    
    Parameters
    ----------
    Parameters to pass as part of steamspy_data_request
    
    appid : integer
        application / game id
    name : string
        application / game name
        
    Return
    ------
    value returned after calling the function
    
    steamspy_json_data : dictionary
        dictionary containing the game data for appid/name.
    
    """
    
    #===============
    
    # set the parameters to get request from steam
    steamspy_url = "https://steamspy.com/api.php"
    steamspy_parameters = {"request": "appdetails", "appid": appid}
    
    # request game details using API
    steamspy_json_data = get_request(steamspy_url, steamspy_parameters)
    
    return steamspy_json_data




# a generic function to save dataframes from batch scrapping into pkl file
def batch_process(fn, app_list, data_filename, begin=0, end=-1, batchsize=1000, pause=2, batch_pause=300):
    """
    Function to get game data in batches and stored to pkl file
    
    Parameters
    ----------
    Parameters to pass as part of batch_process
    
    fn : function
        Function used to scrap data
    app_list : Dataframe
        dataframe containing app_id and game_name
    data_filename : string
        folder/file path and name of file. E.g. '../data/name.pkl'
    begin : integer
        starting index of scrapping. Default is 0. 
    end : integer
        last index of scrapping. Default to -1
    batchsize : integer
        Size of each batch iteration. Default is 1000.
    pause : integer
        value of pause time in seconds for each scrapping. Default is 2 seconds.
    batch_pause : integer
        value of pause time in seconds for each batch. Default is 300 seconds
        
    Return
    ------
    value returned after calling the function
    
    None
        a pkl file is generated after the running the function
    """
        
    #===============
    
    print(f'Starting at index {begin}\n')
    
    # if user did not define where to stop, by default, process all apps in app_list
    if end == -1:
        end = app_list.shape[0]
    
    # generate list of batch begin and end points
    batches = [i for i in range(begin, end, batchsize)]
    # if end not in batches, append it in
    if batches[-1] != end:
        batches.append(end)
    
    # counter - number of games written
    game_written = 0
    
    for i in range(len(batches)-1):
        
        # set start and stop value of batch i
        start = batches[i]
        stop = batches[i+1]
        
        # feedback to user data is being scrapped
        print(f'\rStarting lines {start} to {stop-1} scrapping                        ', end='')
        
        # get dataframe of game_data for batch i
        game_data = get_game_data(start, stop, fn, app_list, pause)
        
        # update counter
        game_written += game_data.shape[0]
        
        # feedback to user data has been collected for export
        print(f'\rData exporting for lines {start} to {stop-1}                        ', end='')
        
        # save (append) game_data into data_filename
        temp = pd.read_pickle(data_filename)          # read original datafile
        game_data = pd.concat([temp, game_data], ignore_index=True)   # combine original with newly scrapped
        pkl_output(data_filename, game_data)   # save pickle file
        
        # feedback to user data being scrapped
        print(f'\rData exported for lines {start} to {stop-1}                        ')
        
        # rest before next batch
        time.sleep(batch_pause)
        
    print(f'\nAll batches complete. {game_written} games extracted')
    
    return None