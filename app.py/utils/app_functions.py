import pandas as pd
import requests
from PIL import Image
from io import BytesIO

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

