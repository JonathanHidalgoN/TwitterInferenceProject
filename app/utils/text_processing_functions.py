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

def delete_words(text, black_list):
    """
    Delete words from a text.
    Args:
        text (str): The text to delete words from.
        black_list (list): The list of words to delete.
    Returns:
        str: The text without the words in the black list.
    """
    if black_list == []:
        return text
    pattern = re.compile(r'\b(' + r'|'.join(black_list) + r')\b\s*')
    text = pattern.sub('', text)
    return text

def count_occurrences(text,black_list = [], top_n = 10):
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
    cleaned_text = clean_text(text)
    cleaned_text = delete_words(cleaned_text, black_list)
    words_times = Counter(cleaned_text.split())
    return words_times.most_common(top_n)

def get_occurences(db,username,character ,n = 1000):
    """
    Get the hashtags of a user.
    Args:
        db (Database): The database object.
        username (str): The username of the user.
        n (int): The number of tweets to get the text of.
    Returns:
        list: The hashtags of the user.
    """
    #Working on this to work do not commit now 
    tweet = get_tweets_text(db,username, n)
    compilation = []
    match = re.findall(r'\b{character}\w+'.format(character = character), tweet)
    if match != []:
        compilation.append(match)
    return compilation

