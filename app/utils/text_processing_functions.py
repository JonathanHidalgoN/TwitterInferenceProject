import re
from collections import Counter

def clean_text(original_text):
    """Clean the text of a tweet.
    Args:
        original_text (str): The text of the tweet.
    Returns: 
        text: The cleaned text of the tweet.   
    """
    text = original_text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "that is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"n'", "ng", text)
    text = re.sub(r"'bout", "about", text)
    text = re.sub(r"'til", "until", text)
    text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", text)
    text = re.sub(r"http\S+", "", text)
    return text

def get_tweets_text(db,username, n = 1_000):
    """Get the text of the tweets of a user.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
        n (int): The number of tweets to get the text of.
    Returns:
        list: The text of the tweets of the user.
    """
    query = "\
    select t.content from Tweets as t\
    left join Users as u\
    on u.id = t.user_id\
    where u.username = '{}'\
    order by t.id desc\
    limit {};\
    ".format(username, n)
    tweets = db.get_values(query)
    tweets = [tweet[0] for tweet in tweets]
    return " ".join(tweets)
    return tweets

def delete_words(text, black_list):
    """
    Delete useless words.
    Args:
        text (str): text to clean
    Returns:
        text (str): cleaned text
    """
    re_banned_words = re.compile(r"\b(" + "|".join(black_list) + ")\\W", re.I)
    return re_banned_words.sub("", text)

def count_occurrences(db,username, n = 1_000, black_list = [], top_n = 10):
    """
    Count the number of occurrences of each word in a column.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
        n (int): The number of tweets to get the text of.
        black_list (list): The list of words to delete.
        Returns:
        Counter: The number of occurrences of each word.
    """
    text = get_tweets_text(db,username, n)
    cleaned_text = clean_text(text)
    cleaned_text = delete_words(cleaned_text, black_list)
    words_times = Counter(cleaned_text.split())
    return words_times.most_common(top_n)