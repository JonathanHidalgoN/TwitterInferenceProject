import pytest
from tweets_pipeline.database import Database
from test_options import database_options

class TestDatabase:
    '''
    This test is used to check if all methods are working correctly in the database class,
    testing the connection, the get_values method and the get_values_error method. Note that
    we need to import database_options from the options file in the options folder.
    '''    
    def setup_method(self):
        """
        Setup methos to instantiate the database class
        """
        self.database = Database(database_options)

    def test_connet_to_database(self):
        """
        This test is used to check if the connect method is working correctly
        """
        try:
            self.connet_to_database = self.database.connect()
            return True
        except:
            return False

    def test_get_values(self):
        """
        This test is used to check if the get_values method is working
        """
        try:
            self.database.get_values("SELECT * FROM TestTable limit 1")
            return True
        except:
            return False

    def test_get_values_error(self):
        """
        This test is used to check if the get_values method raises an error when the query is wrong
        """
        no_table_name = "I_don't_exist"
        statement = "SELECT * FROM {};".format(no_table_name)
        with pytest.raises(Exception):
            self.database.get_values(statement)
    
    def test_get_values2(self):
        """
        This test is used to check if the get_values method is working correctly
        """
        values = self.database.get_values("SELECT * FROM TestTable")
        assert values is not None
        print(values)
        assert len(values[0]) == 3
        assert values[0][0] == 1
        assert values[0][1] == 1
        assert values[0][2] == "soy un test"
        

if __name__ == "__main__":
    import subprocess
    subprocess.call(['pytest', str(__file__)])