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
        _tweets_generator : generator of tweets
    """

    def __init__(self):
        self.database_options = None
        self.database = None
        self.now = datetime.now()
        self.scraper_options = None
        self.cursor = None
        self._tweets_generator = None

    def _connect_to_database(self, database_options):
        """
        This method is used to connect to the database
        Args :
            database_options : dictionary containing database options
        """
        self.database_options = database_options
        self.database = Database(self.database_options)
        self.database.connect()

    def _assing_tweets_generator(self):
        """
        This method is used to assign a generator of tweets to the object, this way
        the query is only executed once
        """
        to_search = self.scraper_options["query"]
        self._tweets_generator = sntwitter.TwitterSearchScraper(to_search).get_items()
        
    def scrape_tweets(self, num_tweets = None):
        """
        This method is used to scrape tweets from twitter and store them in the database
        Args :
            num_tweets : number of tweets to scrape
        Returns :
            tweets : list of tweets scraped
        """
        tweets = []
        if num_tweets is None:
            num_tweets = self.scraper_options["number_of_tweets"]
        for i, tweet in enumerate(self._tweets_generator):
            try:
                if i >= num_tweets:
                    break
                tweets.append(tweet)
            except:
                break
        return tweets

    def _check_user_in_database(self, username):
        """
        This method is used to check if a user is already in the database
        Args :
            username : username of the user to check
        Returns :
            True if the user is not in the database, False otherwise
        """
        query = f"SELECT * FROM Users WHERE username = '{username}'"
        result = self.database.get_values(query)
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
            unique_users.append(tweet.user.username)
        unique_users = list(set(unique_users))
        return unique_users

    def scrape_user(self, username):
        """
        This method is used to scrape users from twitter and store them in the database
        Args :
            username : username of the user to scrape
        Returns :
            user_info : object containing user information
        """
        try:
            user_info = sntwitter.TwitterUserScraper(username)._get_entity()
            if user_info is None:
                return None
            else:
                return user_info
        except KeyError:
            return None

    def format_insert_statement(self, table_name, values):
        """
        This method is used to format an insert statement
        Args :
            table_name : name of the table to insert into
            values : list of values to insert
        Returns :
            insert_statement : string containing the insert statement
        """
        formated_values = "%r" % (tuple(values),)
        if table_name == "Users":
            statement = f"INSERT INTO {table_name}\
                        (username, followers, friends, creation_date, verified, favs, aditionalinfo)\
                        VALUES {formated_values}"
        elif table_name == "Usersinfo":
            statement = f"INSERT INTO {table_name}\
                        (description, displayname, location, profile_image_url)\
                        VALUES {formated_values}"
        elif table_name == "Tweets":
            statement = f"INSERT INTO {table_name}\
                        (content, favs, retweets, quotes, date_ref, user_id, query_id)\
                        VALUES {formated_values}"
        elif table_name == "Querys":
            statement = f"INSERT INTO {table_name}\
                        (query, date_time, num_tweets)\
                        VALUES {formated_values}"
        elif table_name == "Tweetsdate":
            statement = f"INSERT INTO {table_name}\
                        (date_time, day,  month, year)\
                        VALUES {formated_values}"
        return statement + ";"

    def insert_into_database(self, table_name, values):
        """
        This method is used to insert values into a table in the database
        Args :
            table_name : name of the table to insert into
            values : list of values to insert
        """
        insert_statement = self.format_insert_statement(table_name, values)
        self.database.execute_query(insert_statement)

    def find_last_id(self, table_name):
        """
        This method is used to find the last id of a table in the database
        Args :
            table_name : name of the table to find the last id
        Returns :
            last_id : last id of the table
        """
        query = f"SELECT MAX(id) from {table_name}"
        result = self.database.get_values(query)
        return result[0][0]

    def fill_users_tables(self, unique_users):
        """
        This method is used to fill the users tables in the database.
        When an user is not found, but a tweet from this user is found, the user is added to the database with username and 
        default values, this can happen if an user change username.
        Args :
            unique_users : list of unique users
        """
        userinfo_table_name = "Usersinfo"
        users_table_name = "Users"
        for user in unique_users:
            is_user_in_database = self._check_user_in_database(user)
            if is_user_in_database is False:
                next
            else:
                user_info = self.scrape_user(user)
                if user_info is not None:
                    usersinfo_values = [
                        user_info.description,
                        user_info.displayname,
                        user_info.location,
                        user_info.profileImageUrl,
                    ]
                else:
                    usersinfo_values = ["None", "None", "None", "None"]
                self.insert_into_database(userinfo_table_name, usersinfo_values)
                if user_info is not None:
                    users_values = [
                        user,
                        user_info.followersCount,
                        user_info.friendsCount,
                        user_info.created.strftime("%Y-%m-%d"),
                        user_info.verified,
                        user_info.favouritesCount,
                        self.find_last_id(userinfo_table_name),
                    ]
                else:
                    users_values = [user, 0, 0, "9999-12-31", 0, 0, self.find_last_id(userinfo_table_name)]
                self.insert_into_database(users_table_name, users_values)

    def count_tweets(self, query_id):
        """
        This method is used to count the number of tweets in a query
        Args :
            query_id : id of the query
        Returns :
            num_tweets : number of tweets in the query
        """
        query = f"SELECT COUNT(*) FROM Tweets WHERE query_id = {query_id}"
        result = self.database.execute_query(query)
        if result is None:
            return 0
        else:
            return result[0][0]
    
    def fill_query_table(self, query):
        """
        This method is used to fill the query table in the database
        Args :
            query : query to insert
        """
        query_table_name = "Querys"
        query_values = [query, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0]
        self.insert_into_database(query_table_name, query_values)

    def find_user_id(self,username):
        """
        This method is used to find the id of a user in the database
        Args :
            username : username of the user
        Returns :
            user_id : id of the user
        """
        query = f"SELECT id FROM Users WHERE username = '{username}'"
        result = self.database.get_values(query)
        return result[0][0]
    
    def fill_tweets_table(self, tweets):
        """
        This method is used to fill the tweets table in the database
        Args :
            tweets : list of tweets to insert
        """
        tweets_table_name = "Tweets"
        tweetsdate_table_name = "Tweetsdate"
        for tweet in tweets:
            tweetsdate_values = [
                tweet.date.strftime("%Y-%m-%d %H:%M:%S"),
                tweet.date.day,
                tweet.date.month,
                tweet.date.year,
            ]
            self.insert_into_database(tweetsdate_table_name, tweetsdate_values)
            tweets_values = [
                tweet.content,
                tweet.likeCount,
                tweet.retweetCount,
                tweet.quoteCount,
                self.find_last_id(tweetsdate_table_name),
                self.find_user_id(tweet.username),
                self.find_last_id("Querys"),
            ]
            self.insert_into_database(tweets_table_name, tweets_values)
    
    def count_number_of_tweets(self,query_id):
        """
        This method is used to count the number of tweets in a query
        Args :
            query_id : id of the query
        Returns :
            num_tweets : number of tweets in the query
        """
        query = f"SELECT COUNT(*) FROM Tweets WHERE query_id = {query_id}"
        result = self.database.get_values(query)
        if result is None:
            return 0
        else:
            return result[0][0]


    def update_query_table(self, query_id, num_tweets):
        """
        This method is used to update the query table in the database
        Args :
            query_id : id of the query
            num_tweets : number of tweets in the query
        """
        query = f"UPDATE Querys SET num_tweets = {num_tweets} WHERE id = {query_id}"
        self.database.execute_query(query)



    def _manage_scraping(self,batch_size = 1000, verbose = False):
        pass
    
    def start_scraping(self, scraper_options = None, database_options = None, **kwargs):
        """
        This method is used to start the scraper
        step 1 : connect to the database
        step 2 : scrape tweets
        step 3 : create a list of unique users
        step 4 : fill the users tables
        step 5 : fill the query table
        step 6 : fill the tweets table
        step 7 : count the number of tweets scraped
        """
        self._connect_to_database(database_options)
        self.scraper_options = scraper_options
        self._assing_tweets_generator()
        tweets = self.scrape_tweets()
        unique_users = self.check_unique_users(tweets)
        self.fill_users_tables(unique_users)
        self.fill_query_table(scraper_options["query"])
        self.fill_tweets_table(tweets)
        last_query_id = self.find_last_id("Querys")
        self.update_query_table(last_query_id, self.count_number_of_tweets(last_query_id))



if __name__ == "__main__":
    from tweets_pipeline.options import database_options, scraper_options
    scraper = TweetScraper()
    scraper.start_scraping(scraper_options, database_options)
    
    