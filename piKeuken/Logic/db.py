""" Class for the database """
import sqlite3
import sys
import os
import logging

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)
logging.basicConfig(filename="piKeuken/data/logging_db.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


""" https://stackoverflow.com/questions/534839/how-to-create-a-guid-uuid-in-python """


class DB:
    def __init__(self):
        try:
            self.database_location = "piKeuken/data/db"
            """ Create the tables if they don't exist'"""
            self.create_start_tables()
        except Exception as ex:
            logging.error(ex)

    def create_start_tables(self):
        try:
            #""" Create the notification-table """
            self.execute(
                "CREATE TABLE IF NOT EXISTS tb_notifications(id VARCHAR(41) PRIMARY KEY, name VARCHAR(91), message VARCHAR(131), datetime DATETIME DEFAULT CURRENT_TIMESTAMP)")
            #""" Create the table where you can view wich persons has read the messages """
            self.execute(
                "CREATE TABLE IF NOT EXISTS tb_notifications_viewed(notification_id VARCHAR(41), user_id int, datetime DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(notification_id) REFERENCES tb_notifications(id))")
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def execute(self, command, par=(), read=False):
        try:
            """ Open a connections with the database """
            db = sqlite3.connect(self.database_location)
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(command, par)
            db.commit()
            """ Check if the data must be returned """
            if read:
                return cursor.fetchall()
        except Exception as ex:
            logging.error(ex)
            db.rollback()
            raise ex
        finally:
            """ Close the database connection """
            db.close()