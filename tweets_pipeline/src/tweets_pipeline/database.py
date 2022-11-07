# This script contains Database class, which is used to connect to the database and perform operations on it.

import mysql.connector


class Database:
    """
    This class is used to connect to the database and perform operations on it.
    Args :
        database_options : dictionary containing database options
    Attributes :
        connection : connection to the database
        cursor : cursor to the database
        connection_status : boolean value indicating if connection is established or not
    """

    def __init__(self, database_options):
        self.database_options = database_options
        self.connection = None
        self.cursor = None
        self.connection_status = False

    def connect(self):
        """
        This method is used to connect to the database, establish a cursor and set connection status to True
        Returns :
            connection (mysql.connector.connection.MySQLConnection) : connection to the database
        """
        try:
            self.connection = mysql.connector.connect(**self.database_options)
            self.connection_status = True
            return self.connection
        except Exception as e:
            raise e

    def check_connection(self):
        """
        This method is used to check if connection is established or not
        if not it tries to connect to the database
        """
        if self.connection_status is False:
            self.connect()

    def disconnect(self):
        """
        This method is used to disconnect from the database
        """
        try:
            self.connection.close()
            self.cursor.close()
        except Exception as e:
            raise e

    def execute_query(self, query):
        """
        This method is used to execute a query on the database
        Args :
            query : query to be executed
        """
        self.check_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

    def get_values(self, query):
        """
        This method is used to execute a query on the database and return the results
        Args :
            query (str): query to be executed
        Returns :
            results (list) : list of tuples containing the results of the query
        """
        self.check_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
