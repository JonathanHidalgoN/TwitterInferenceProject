import text_processing_functions 

def tweets_to_text(db, query, clean_tweets = False, path = "tweets.txt", delimiter = " "):
    """Get the tweets from a query and return them as a text.
    Args:
        db (Database): The database object.
        query (str): The query to get the tweets from.
        clean_tweets (bool): If the tweets should be cleaned.
    Returns:
        str: The tweets as a text.
    """    
    tweets = db.get_values(query)
    tweets = [tweet[0] for tweet in tweets]
    if clean_tweets:
        tweets = [text_processing_functions.clean_text(tweet) for tweet in tweets]
    with open(path, "w") as f:
        for tweet in tweets:
            f.write(tweet + delimiter)
    return None    

if __name__ == "__main__":
    from tweets_pipeline.database import Database
    from options import database_options
    db = Database(database_options)
    query = "select content from Tweets order by id desc;"
    tweets = tweets_to_text(db, query, clean_tweets = True, path = "tweets.txt", delimiter = "|-|")
    print(tweets)
