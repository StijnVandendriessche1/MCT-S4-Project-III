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
        try:
            self.notification_queue = notification_queue
            self.db = DB()
            self.influxdb = Influxdb()
            self.send_mail = SendMail()
            self.hour_notification = timedelta(hours=16, minutes=13)
            """ Status:
                    -   0   ==> Nothing
                    -   1   ==> Notification that the dishwasher must be filled
                    -   3   ==> Running
            """
            self.status = 0
            self.hour_on = datetime.now()
            self.duration = timedelta(hours=1, minutes=31)
            self.ai_status = True
            self.mail_person = ["tibo.van.craenenbroeck@student.howest.be"]
            self.get_settings()
        except Exception as e:
            logging.error(e)

    def start(self):
        try:
            """ Create a thread that checks if the dishwasher is on and if de server must send a notification """
            t_dishwasher = Thread(target=self.check_state)
            t_dishwasher.start()
        except Exception as e:
            logging.error(e)

    def check_state(self):
        try:
            while True:
                try:
                    if self.ai_status:
                        """ Check if the dishwasher is on """
                        vibration = self.check_vibration()
                        """ Check if the dishwasher is on """
                        if vibration and self.status == 0:
                            """ Send notification that the dishwasher is started """
                            self.notification_queue.put(
                                {"name": "🍽", "message": "Dishwasher is cleaning! 🧺🧺🧺"})
                            self.status = 3
                            self.hour_on = datetime.now()
                            """ Change the settings in the database """
                            self.change_settings({"dishwasher_status": self.status})
                            self.change_settings({"dishwasher_hour_on": self.hour_on})
                        if self.status == 0 and datetime.now() >= self.hour_notification:
                            self.notification_queue.put(
                                {"name": "🍽", "message": "Don't forget to fill in the dishwasher! 💩"})
                            self.status = 1
                            """ Send is to a person """
                            self.send_mail.send_message( "The dishwasher needs you!","Don't forget to fill in the dishwasher", self.mail_person)
                            """ Change the settings in the database """
                            self.change_settings({"dishwasher_status": self.status})
                        elif self.status == 3 and (self.hour_on + self.duration) >= datetime.now():
                            """ Check if the dishwasher is done """
                            self.notification_queue.put(
                                {"name": "🍽", "message": "The Dishwasher is empty! Time to empty it! 😇"})
                            self.status = 0
                            """ Change the settings in the database """
                            self.change_settings({"dishwasher_status": self.status})
                except Exception as e:
                    logging.error(e)
                sleep(61)
        except Exception as e:
            logging.error(e)
            raise e

    def check_vibration(self):
        try:
            query = '|> range(start: -3m, stop: now()) |> filter(fn: (r) => r["_measurement"] == "sensor_data") |> filter(fn: (r) => r["host"] == "kitchen") |> filter(fn: (r) => r["_value"] == "dishwasher") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> tail(n: 3)'
            vibration_intensity_data = self.influxdb.get_data(query, False)
            if not vibration_intensity_data.empty:
                return True
            return False
        except Exception as e:
            logging.error(e)
            raise e

    def get_settings(self):
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
                self.status = int(settings[settings["name"] == "dishwasher_status"]["value"])
                self.hour_on = datetime.strptime(settings[settings["name"] == "dishwasher_hour_on"]["value"].iloc[0], f"%Y-%m-%d %H:%M:%S.%f")
                self.duration = self.parse_time(settings[settings["name"] == "dishwasher_duration"]["value"].iloc[0])
                self.mail_person = []
                self.mail_person.append(settings[settings["name"] == "dishwasher_email"]["value"].iloc[0])
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def parse_time(self, time_str):
        try:
            split_time = time_str.split(':')
            return timedelta(hours=int(split_time[0]), minutes=int(split_time[1]))
        except Exception as e:
            logging.error(e)
            raise e
    
    def get_str_time_form_timedelta(self, time):
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
        try:
            for setting in settings_update:
                self.change_settings_db(
                    setting, settings_update[setting], user_id)
            self.get_settings()
        except Exception as ex:
            logging.error(ex)
            raise ex

    def change_settings_db(self, name, value, user_id):
        try:
            self.db.execute(f"UPDATE tb_settings SET value=:value, user_id=:user_id WHERE name=:name", {
                            "name": name, "value": value, "user_id": user_id})
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def get_dishwasher_settings(self):
        try:
            data = {}
            data["dishwasher_hour_notification"] = self.get_str_time_form_timedelta(self.hour_notification)
            data["dishwasher_duration"] = self.get_str_time_form_timedelta(self.duration)
            data["dishwasher_email"] = self.mail_person[0]
            return data
        except Exception as ex:
            logging.error(ex)
            raise ex
