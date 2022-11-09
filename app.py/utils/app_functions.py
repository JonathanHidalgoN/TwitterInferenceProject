import pandas as pd

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
    from tweets as t left join users as u\
    on u.id = t.user_id\
    group by t.user_id\
    order by num desc\
    limit {n};\
    "
    values = db.get_values(query)
    df = pd.DataFrame(values, columns=['username', 'num_tweets', 'followers', 'verified'])
    return df

def average_col(db,column, table, aditional = None):
    if aditional == None :
        aditona = ""
    query = "select avg({}) from {} {}".format(column, table, aditional)
    values = db.get_values(query)
    return values[0][0]

def examine_user(db, username):
    general_info = "\
    select u.username, u.followers, u.verified,u.favs ,count(*) as num \
    from tweets as t left join users as u\
    on u.id = t.user_id\
    where u.username = '{}'\
    group by t.user_id limit 1;\
    ".format(username)
    general_info = db.get_values(general_info)
    general_info = pd.DataFrame(general_info, columns=['username', 'followers', 'verified',"likes" ,'num_tweets'])
    general_info = general_info.set_index('username')
    general_info = general_info.T
    general_info = general_info.rename(columns={username: f'Information of {username}'})
    return general_info

if __name__ == "__main__":
    from tweets_pipeline.database import Database
    database_options = {
    "host": "localhost",
    "user": "root",
    "password": "Jonathan500*",
    "database": "twitterdb",
    "connection_timeout": 20 * 60
    }
    db = Database(database_options)
    db.connect()
    df = users_with_most_tweets(db)
    print(df)