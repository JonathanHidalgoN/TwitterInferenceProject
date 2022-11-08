from tweets_pipeline.tweets_scraper import TweetScraper
import pytest
from test_options import database_options, scrape_options


class TestScrapper:

    def setup_method(self):
        """
        Setup method to instantiate the scraper class
        """
        self.scraper = TweetScraper()

    def test_connect_to_database(self):
        """
        This test is used to check if the connect method is working correctly
        """
        try:
            self.scraper._connect_to_database(database_options=database_options)
            return True
        except:
            return False

    def test_scrape_users(self):
        """
        This test is used to check if the scrape_users method is working correctly
        """
        fist_username = "ElonMusk"
        no_username = "__I_don't_exist__"
        first_user = self.scraper.scrape_user(username=fist_username)
        with pytest.raises(Exception):
            self.scraper.scrape_user(username=no_username)
        assert first_user is not None
        

if __name__ == "__main__":
    import subprocess
    subprocess.call(['pytest', str(__file__)])