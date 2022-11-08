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

if __name__ == "__main__":
    from tweets_pipeline.database import Database
    db = Database(database_options)
    db.connect()
    df = users_with_most_tweets(db)
    print(df)