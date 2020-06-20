""" Class for the database """
import sqlite3
import sys
import os
import logging
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class DB:
    def __init__(self):
        """Init of the class for setting up the basicConfig
        """        
        try:
            self.database_location = f"{BASE_DIR}/data/ootf.db"
            """ Create the tables if they don't exist'"""
            self.create_start_tables()
        except Exception as ex:
            logging.error(ex)

    def create_start_tables(self):
        """This function creates all the tables if they don't exist'

        Raises:
            Exception: Error-message
        """        
        try:
            #""" Create the notification-table """
            self.execute(
                "CREATE TABLE IF NOT EXISTS tb_notifications(id VARCHAR(41) PRIMARY KEY, name VARCHAR(91), message VARCHAR(131), datetime DATETIME DEFAULT CURRENT_TIMESTAMP)")
            #""" Create the table where you can view wich persons has read the messages """
            self.execute(
                "CREATE TABLE IF NOT EXISTS tb_notifications_viewed(notification_id VARCHAR(41), user_id int, datetime DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(notification_id) REFERENCES tb_notifications(id))")
            #""" Create the settings_tables """
            self.execute(
                "CREATE TABLE IF NOT EXISTS tb_settings(name VARCHAR(91) PRIMARY KEY, value VARCHAR(255), user_id int, datetime DATETIME DEFAULT CURRENT_TIMESTAMP)")
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def execute(self, command, par=(), read=False):
        """This function execute the query. It can be return a dataframe. If something went wrong, it will do a rollback.

        Args:
            command (string): This must be the query
            par (tuple, dict), optional): This var can be a dictionary, list or a tuple. This are the parameters for the query. Defaults to ().
            read (bool, optional): If the query must be return a dataframe, this must be set to True. Defaults to False.

        Raises:
            ex: Error-message

        Returns:
            Dataframe: If the read-bool is set on True, this will be return a dataframe
        """        
        try:
            # Open a connections with the database
            db = sqlite3.connect(self.database_location)
            if read:
                results = pd.read_sql_query(command, db, params=par)
                return results
            else:
                db.row_factory = sqlite3.Row
                cursor = db.cursor()
                cursor.execute(command, par)
                db.commit()
        except Exception as ex:
            logging.error(ex)
            db.rollback()
            raise ex
        finally:
            # Close the database connection
            if read == False:
                cursor.close()
            db.close()
