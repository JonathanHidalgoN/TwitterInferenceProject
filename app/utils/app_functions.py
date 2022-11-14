import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import seaborn as sns
import datetime as dt
import matplotlib.pyplot as plt
from utils import text_processing_functions as text_functions 
from streamlit import write as stwrite
from streamlit import markdown as stmarkdown
import numpy as np
from random import choice as randomchoice

def users_with_most_tweets(db, n=10):
    """Get the users with the most tweets in the database.
    Args:
        db (Database): The database object.
        n (int): The number of users to return.
    Returns:
        DataFrame: The users with the most tweets in the database.
    """    
    query = f"\
    select u.username, count(*) as num,\
    u.followers, u.verified\
    from Tweets as t left join Users as u\
    on u.id = t.user_id\
    group by t.user_id\
    order by num desc\
    limit {n};\
    "
    values = db.get_values(query)
    df = pd.DataFrame(values, columns=['username', 'num_tweets', 'followers', 'verified'])
    return df

def average_col(db,column, table, aditional = None):
    """Get the average of a column in a table.
    Args:
        db (Database): The database object.
        column (str): The column to get the average of.
        table (str): The table to get the average from.
        aditional (str): An aditional statement to add to the query.
    Returns:
        float: The average of the column in the table.
    """
    if aditional == None :
        aditional = ""
    query = "select avg({}) from {} {}".format(column, table, aditional)
    values = db.get_values(query)
    return values[0][0]

def examine_user(db, username):
    """Get general information about a user.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
    Returns:
        DataFrame: The general information about the user.
    """ 
    general_info = "\
    select u.username, u.followers, u.verified,u.favs ,count(*) as num \
    from Tweets as t left join Users as u\
    on u.id = t.user_id\
    where u.username = '{}'\
    group by t.user_id limit 1;\
    ".format(username)
    general_info = db.get_values(general_info)
    general_info = pd.DataFrame(general_info, columns=['username', 'followers', 'verified',"likes" ,'number of tweets'])
    general_info = general_info.set_index('username')
    general_info = general_info.T
    general_info = general_info.rename(columns={username: f'Information of {username}'})
    return general_info

def get_image_of_user(db,username):
    """Get the profile image of a user.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
    Returns:
        Image: The profile image of the user.
    """
    find_id_query = "select aditionalinfo from Users where username = '{}'".format(username)
    user_aditional_info_id = db.get_values(find_id_query)[0][0]
    user_statement = "select profile_image_url from Usersinfo where id = {}".format(user_aditional_info_id)
    user_image_url = db.get_values(user_statement)[0][0]
    response = requests.get(user_image_url, stream=True)
    img = Image.open(BytesIO(response.content))
    return img

def get_tweets_dates(db,username, n = 1_000):
    """Get the dates of the tweets of a user.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
        n (int): The number of tweets to get the dates of.
    Returns:
        list: The dates of the tweets of the user.
    """
    query = "\
    select d.date_time from Tweetsdate as d\
    left join Tweets as t\
    on d.id = t.date_ref\
    left join Users as u\
    on u.id = t.user_id\
    where u.username = '{}'\
    order by d.date_time desc\
    limit {};\
    ".format(username, n)
    values = db.get_values(query)
    return values

def create_dates_dashboard(db,username,n = 1_000, group_by = "day"):
    """Create a dashboard of the dates of the tweets of a user.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
        n (int): The number of tweets to get the dates of.
        group_by (str): The way to group the dates.
    Returns:
        Figure: The dashboard of the dates of the tweets of the user.
    """
    dates = get_tweets_dates(db,username,n)
    dates = [date[0].date() for date in dates]
    dates = pd.DataFrame(dates, columns=['date'])
    dates['date'] = pd.to_datetime(dates['date'])
    #count per day
    if group_by == "day":
        dates = dates.groupby(dates['date'].dt.date).size().reset_index(name='counts')
    #count per month
    elif group_by == "month":
        dates = dates.groupby(dates['date'].dt.to_period("M")).size().reset_index(name='counts')
    #graph
    fig, ax = plt.subplots(figsize=(15, 5))
    sns.lineplot(x="date", y="counts", data=dates, ax=ax)
    ax.set_title(f"Number of tweets per {group_by} of {username}")
    ax.set_xlabel(f"Date ({group_by})")
    ax.set_ylabel("Number of tweets")
    return fig

def create_common_words_graph(db,username,n = 1000,black_list = [],top_n = 10):
    """Create a bar plot of the most common words in the tweets of a user.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
        n (int): The number of tweets to get the words of.
        black_list (list): The words to ignore.
        top_n (int): The number of words to show.
    Returns:
        Figure: The dashboard of the most common words in the tweets of the user.
    """
    text = text_functions.get_tweets_text(db,username,n)
    common_words = text_functions.count_occurrences(text,black_list,top_n)
    words = [word[0] for word in common_words]
    counts = [word[1] for word in common_words]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.set_theme(style="ticks")
    sns.set_style("darkgrid")
    sns.barplot(y=words, x=counts, ax=ax,
                palette="pastel", linewidth=2.5, color = "red")
    ax.set_title(f"Most common words of {username}")
    ax.set_ylabel("Words")
    ax.set_xlabel("Number of occurrences")
    return fig
    
            
def get_a_column(db,table,col,aditional = ""):
    """Get a column from a table.
    Args:
        db (Database): The database object.
        table (str): The table to get the column from.
        col (str): The column to get.
        aditional (str): Aditional information to add to the query.
    Returns:
        list: The values of the column.
    """
    query = f"select {col} from {table} {aditional}"
    values = db.get_values(query)
    return values

def display_distribution(db,col, n = 1000):
    """Display the distribution of a column.
    Args:
        db (Database): The database object.
        col (str): The column to display the distribution of.
        n (int): The number of tweets to get the words of.
    Returns:
        Figure: The dashboard of the distribution of the column.
    """
    colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "grey", "black"]
    if col !="number of words per tweet":
        favs = get_a_column(db,"Tweets",f"{col}",f"limit {n}")
        favs = [fav[0] for fav in favs]
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.set_style("darkgrid")
        ax.set_xlim(0, np.percentile(favs, 90))
        sns.histplot(favs, ax=ax, color = randomchoice(colors) , palette="pastel", kde=True)
        ax.set_title(f"Distribution of {col}")
        ax.set_ylabel("Number of tweets")
        ax.set_xlabel(f"Number of {col}")
    else : 
        words = get_a_column(db,"Tweets","content",f"limit {n}")
        words = [len(word[0].split()) for word in words]
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.set_style("darkgrid")
        ax.set_xlim(0, np.percentile(words, 90))
        sns.histplot(words, ax=ax, color = randomchoice(colors), palette="pastel", kde=True)
        ax.set_title(f"Distribution of {col}")
        ax.set_ylabel("Number of tweets")
        ax.set_xlabel(f"Number of {col}")
    return fig

    
def _add_space(n = 5):
    """Add a space.
    Args:
        n (int): The number of spaces to add.
    """
    for _ in range(n):
        stwrite("")


if __name__ == "__main__":
    from app_options import database_options
    from tweets_pipeline.database import Database
    db = Database(database_options)
    db.connect()
    username = "elonmusk"
    dates = get_tweets_dates(db, username)
    print(dates)









