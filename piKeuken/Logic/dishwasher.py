import logging
import os
import re
import sys
from datetime import datetime, timedelta
from queue import Queue

import pandas as pd
from threading import Thread

from time import sleep

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.db import DB
from Logic.influxdb import Influxdb
from Logic.send_mail import SendMail

""" Class for the dishwasher """

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


class Dishwasher:
    def __init__(self, notification_queue):
        """The init-function setup the class with default values. He calls the get_settings for getting the new settings.

        Args:
            notification_queue (Queue): This Queue if for adding new notifications to the frontend.
        """        
        try:
            self.update_settings = 0
            self.notification_queue = notification_queue
            self.db = DB()
            self.influxdb = Influxdb()
            self.send_mail = SendMail()
            self.hour_notification = timedelta(hours=16, minutes=13)
            """ Status:
                    -   0   ==> Nothing
                    -   1   ==> Notification that the dishwasher must be filled or the dishwasher is already done
                    -   3   ==> Running
            """
            self.status = 0
            self.hour_on = datetime.now()
            self.duration = timedelta(hours=1, minutes=31)
            self.ai_status = True
            self.mail_person = ["tibo.van.craenenbroeck@student.howest.be"]
            self.get_settings()
            self.start()
        except Exception as e:
            logging.error(e)

    def start(self):
        """This function is for starting a thread. This thread checks if the dishwasher is running and if someone must be started him.
        """        
        try:
            """ Create a thread that checks if the dishwasher is on and if de server must send a notification """
            t_dishwasher = Thread(target=self.check_state)
            t_dishwasher.start()
        except Exception as e:
            logging.error(e)

    def check_state(self):
        # TODO:Check if it works
        """Check_state is a thread-function. He checks the state of the dishwasher and if someone must be started him (after a time)

        Raises:
            e: Error-message
        """        
        try:
            while True:
                try:
                    if self.ai_status and self.update_settings == 0:
                        self.update_settings = 3
                        """ Check if the dishwasher is on """
                        vibration = self.check_vibration()
                        hour_now = datetime.now().hour
                        minute_now = datetime.now().minute
                        time_now = timedelta(hours=hour_now, minutes=minute_now)
                        """ Check if the dishwasher is on """
                        print("hour_on: ", self.hour_on)
                        print("hour_on: ", self.hour_on)
                        print("self.status: ", self.status)
                        print("self.duration: ", self.duration)
                        print("tot: ", (self.hour_on + self.duration))
                        if (vibration and self.status == 0) or (vibration and self.status == 1):
                            """ Send notification that the dishwasher is started """
                            self.notification_queue.put(
                                {"name": "🍽", "message": "Dishwasher is running! 🧺🧺🧺"})
                            self.status = 3
                            self.hour_on = datetime.now()
                            """ Change the settings in the database """
                            self.change_settings({"dishwasher_status": self.status, "dishwasher_hour_on": self.hour_on})
                        elif self.status == 0 and time_now >= self.hour_notification:
                            self.notification_queue.put(
                                {"name": "🍽", "message": "Don't forget to fill in the dishwasher! 💩"})
                            self.status = 1
                            """ Send is to a person """
                            self.send_mail.send_message( "The dishwasher needs you!","Don't forget to fill in the dishwasher", self.mail_person)
                            """ Change the settings in the database """
                            self.change_settings({"dishwasher_status": self.status})
                        elif self.status == 3 and (self.hour_on + self.duration) <= datetime.now():
                            """ Check if the dishwasher is done """
                            self.notification_queue.put(
                                {"name": "🍽", "message": "The Dishwasher is done! Time to empty it! 😇"})
                            self.status = 1
                            """ Change the settings in the database """
                            self.change_settings({"dishwasher_status": self.status})
                        elif self.status == 1 and time_now>= timedelta(hours=5, minutes=31) and time_now <= timedelta(hours=5, minutes=35):
                            """ Reset the dishwasher status """
                            self.status = 0
                            self.change_settings({"dishwasher_status": self.status})
                except Exception as e:
                    logging.error(e)
                self.update_settings = 0
                sleep(61)
        except Exception as e:
            logging.error(e)
            raise e

    def check_vibration(self):
        """This function checks if he detects a vibration.

        Raises:
            e: Error-message

        Returns:
            bool: It returns true if he detects a vibration, else false
        """        
        try:
            query = '|> range(start: -3m, stop: now()) |> filter(fn: (r) => r["_measurement"] == "sensordata") |> filter(fn: (r) => r["host"] == "Kitchen") |> filter(fn: (r) => r["_value"] == "Detect") |> sort(columns: ["_time"], desc: true)'
            vibration_intensity_data = self.influxdb.get_data(query, False)
            if not vibration_intensity_data.empty:
                return True
            return False
        except Exception as e:
            logging.error(e)
            raise e

    def get_settings(self):
        """This function gets the last settings of the dishwasher. If there are no settings yet, he add the default to the SQLite

        Raises:
            ex: Error-message if someting went wrong
        """        
        try:
            """ Get the dishwasher_settings from the database """
            settings = self.db.execute(
                '''SELECT name, value FROM tb_settings WHERE name="dishwasher_hour_notification" OR name="dishwasher_status" OR name="dishwasher_hour_on" OR name="dishwasher_duration" OR name="dishwasher_email"''', (), True)
            """ Check the table is empty """
            if settings.shape[0] == 0:
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('dishwasher_hour_notification', '{self.hour_notification}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('dishwasher_status', '{self.status}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('dishwasher_hour_on', '{self.hour_on}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('dishwasher_duration', '{self.duration}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('dishwasher_email', '{self.mail_person[0]}', 0)""")
            else:
                """ Change the value of the vars """
                self.hour_notification = self.parse_time(settings[settings["name"] == "dishwasher_hour_notification"]["value"].iloc[0])
                self.status = int(settings[settings["name"] == "dishwasher_status"]["value"].iloc[0])
                self.hour_on = datetime.strptime(settings[settings["name"] == "dishwasher_hour_on"]["value"].iloc[0], f"%Y-%m-%d %H:%M:%S.%f")
                self.duration = self.parse_time(settings[settings["name"] == "dishwasher_duration"]["value"].iloc[0])
                self.mail_person = []
                self.mail_person.append(settings[settings["name"] == "dishwasher_email"]["value"].iloc[0])
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def parse_time(self, time_str):
        """This function converts a string to a timedelta

        Args:
            time_str (string): This must be a time in format: hh:mm or hh:mm:ss

        Raises:
            e: Error-message

        Returns:
            deltatime: This function returns a deltatime
        """        
        try:
            split_time = time_str.split(':')
            return timedelta(hours=int(split_time[0]), minutes=int(split_time[1]))
        except Exception as e:
            logging.error(e)
            raise e
    
    def get_str_time_form_timedelta(self, time):
        """This function converts a deltatime to a string

        Args:
            time (deltatime): The incoming var must be a deltatime

        Raises:
            ex: Error-message

        Returns:
            string: This string has the format: hh:mm:ss
        """        
        try:
            totsec = time.total_seconds()
            h = int(totsec//3600)
            m = int((totsec%3600) // 60)
            sec =int((totsec%3600)%60)
            return f"{h:02}:{m:02}:{sec:02}"
        except Exception as ex:
            logging.error(ex)
            raise ex

    def change_settings(self, settings_update, user_id=0):
        """This function is for changing the settings in the SQLite

        Args:
            settings_update (dict): This must be a dictionary
            user_id (int, optional): This must be the ID of the user (Google Auth). Defaults to 0.

        Raises:
            ex: Error-message
        """        
        try:
            if user_id != 0:
                while self.update_settings == 3:
                    sleep(0.11)
            self.update_settings = 1
            for setting in settings_update:
                self.change_settings_db(
                    setting, settings_update[setting], user_id)
            self.get_settings()
            self.update_settings = 0
        except Exception as ex:
            logging.error(ex)
            raise ex

    def change_settings_db(self, name, value, user_id):
        """This function is for changing the changes in the SQLite

        Args:
            name (string): This must be the name of the item that has to be changed
            value (string): Item that is changed
            user_id (int): This must be the ID of the user (Google Auth)

        Raises:
            ex: Error-message
        """        
        try:
            self.db.execute(f"UPDATE tb_settings SET value=:value, user_id=:user_id WHERE name=:name", {
                            "name": name, "value": value, "user_id": user_id})
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def get_dishwasher_settings(self):
        """This function returns a dict for the frontend

        Raises:
            ex: Error-message

        Returns:
            dicht: Returns dicht with settings
        """
        try:
            data = {}
            data["dishwasher_hour_notification"] = self.get_str_time_form_timedelta(self.hour_notification)
            data["dishwasher_duration"] = self.get_str_time_form_timedelta(self.duration)
            data["dishwasher_email"] = self.mail_person[0]
            return data
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def get_dishwasher_status(self):
        """This function returns a True if the dishwasher is on and False if it is off

        Raises:
            ex: Error-message

        Returns:
            bool: True if it is on, False if it is off
        """        
        try:
            if self.status == 3:
                return True
            else:
                return False
        except Exception as ex:
            logging.error(ex)
            raise ex
