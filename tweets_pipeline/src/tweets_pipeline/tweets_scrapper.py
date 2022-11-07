from tweets_pipeline.database import Database
import snscrape.modules.twitter as sntwitter
from datetime import datetime

class TweetScraper:

    """
    This class is used to scrape tweets from twitter using snscrape, and store them in a database.
    It also scrape user information and store them in the database.
    Attributes :
        database_options : dictionary containing database options
        database : database object
        now : current date and time when the object is created
        scraper_options : dictionary containing scrape options
        cursor : cursor to the database
    """

    def __init__(self):
        self.database_options = None
        self.database = None
        self.now = datetime.now()
        self.scraper_options = None
        self.cursor = None

    def _connect_to_database(self, database_options):
        """
        This method is used to connect to the database, establish a cursor
        Args :
            database_options : dictionary containing database options
        """
        self.database_options = database_options
        self.database = Database(self.database_options)
        self.database.connect()
        self.cursor = self.database.connection.cursor()

    def scrape(self, scraper_options):
        """
        This method is used to scrape tweets and users from twitter and store them in the database
        Args :
            scraper_options : dictionary containing scrape options
        """
        self.scraper_options = scraper_options

    def scrape_tweets(self, num_tweets):
        """
        This method is used to scrape tweets from twitter and store them in the database
        Args :
            num_tweets : number of tweets to scrape
        Returns :
            tweets : list of tweets scraped
        """ 
        tweets = []
        to_search = self.scraper_options['query']
        for i, tweet in enumerate(
            sntwitter.TwitterSearchScraper(to_search).get_items()
        ):
            try:
                if i >= num_tweets:
                    break
                tweets.append(tweet)
            except:
                break
        return tweets

    def _check_user_in_database(self,username):
        """
        This method is used to check if a user is already in the database
        Args :
            username : username of the user to check
        Returns :
            True if the user is not in the database, False otherwise
        """
        query = f"SELECT * FROM Users WHERE username = '{username}'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if len(result) == 0:
            return True
        else:
            return False

    def check_unique_users(self, tweets):
        """
        This method create a list with unique users from a list of tweets
        Args :
            tweets : list of tweets
        Returns :
            unique_users : list of unique users
        """
        unique_users = []
        for tweet in tweets:
            if (tweet.user not in unique_users) and (self._check_user_in_database(tweet.user.username)):
                unique_users.append(tweet.user.username)
        return unique_users




if __name__ == "__main__":
    from options import database_options, scraper_options
    scraper = TweetScraper()
    print(dir(scraper))
    scraper._connect_to_database(database_options)
    scraper.scrape(scraper_options)
    tweets = scraper.scrape_tweets(10)
    unique_users = scraper.check_unique_users(tweets)
    print(unique_users)
