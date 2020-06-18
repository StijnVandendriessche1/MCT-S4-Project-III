""" Class for coffee """
import uuid
import sys
import os
import logging

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.db import DB
from Logic.send_mail import SendMail

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class Coffee:
    def __init__(self, notification_queue):
        try:
            self.ai_status = True
            self.coffee_left = 0
            self.coffee_left_threshold = 3000.0
            self.coffee_ordered = False
            self.coffee_notification_ordered = False
            self.coffee_notification_empty = False
            self.delivery_time = 1
            self.notification_queue = notification_queue
            self.send_mail = SendMail()
            self.db = DB()
            self.mail_supplier = ["tibo.van.craenenbroeck@student.howest.be"]
            self.mail_message = "Beste<br><br>Graag zouden wij 20Kg koffie bestellen bij jullie.<br><br>MVG<br>ML6"
            self.get_settings()
        except Exception as ex:
            logging.error(ex)

    def coffee_checker(self, coffee_left):
        try:
            if self.ai_status:
                """ Change the coffee_left """
                self.coffee_left = coffee_left
                """ Check if the coffee must be ordered """
                if self.coffee_left <= self.coffee_left_threshold and self.coffee_notification_ordered == False:
                    #""" Send a notification when the coffee is ordered"""
                    self.send_mail.send_message(
                        "Bestelling koffie ML6", self.mail_message, self.mail_supplier)
                    self.coffee_notification_ordered = True
                    self.notification_queue.put(
                        {"name": "☕", "message": "🚚 Your coffee is on it's way! 🚚"})
                    self.change_settings({"coffee_notification_ordered": str(self.coffee_notification_ordered)})
                elif self.coffee_left <= 11 and self.coffee_notification_empty == False:
                    #""" Send a notification when the coffee is empty"""
                    self.notification_queue.put(
                        {"name": "☕", "message": "😥 Oh no! Coffee is finished, Time for starbucks 🚶‍♀️"})
                    self.coffee_notification_empty = True
                    self.change_settings({"coffee_notification_empty": str(self.coffee_notification_empty)})
                elif self.coffee_left >=(self.coffee_left_threshold*1.11) and self.coffee_notification_empty:
                    #""" Send a notification that the coffee is full """
                    self.coffee_notification_empty = False
                    self.coffee_notification_ordered = False
                    self.notification_queue.put({"name": "☕", "message": "Your coffee has arrived to the office! 🚚"})
                    self.change_settings({"coffee_notification_empty": str(self.coffee_notification_empty),"coffee_notification_ordered": str(self.coffee_notification_ordered)})
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def check_bool(self, bool_in):
        bool_out = bool_in.iloc[0]
        if bool_out == "True":
            return True
        else:
            return False

    def get_settings(self):
        try:
            """ Get the coffee_settings from the database """
            settings = self.db.execute(
                '''SELECT name, value FROM tb_settings WHERE name="coffee_left_threshold" OR name="coffee_ordered" OR name="coffee_notification_ordered" OR name="coffee_notification_empty" OR name="mail_supplier" OR name="delivery_time" OR name="mail_message"''', (), True)
            """ Check the table is empty """
            if settings.shape[0] == 0:
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('coffee_left_threshold', '{self.coffee_left_threshold}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('coffee_ordered', '{self.coffee_ordered}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('coffee_notification_ordered', '{self.coffee_notification_ordered}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('coffee_notification_empty', '{self.coffee_notification_empty}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('mail_supplier', '{self.mail_supplier[0]}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('delivery_time', '{self.delivery_time}', 0)""")
                self.db.execute(
                    f"""INSERT INTO tb_settings (name, value, user_id) VALUES('mail_message', '{self.mail_message}', 0)""")
            else:
                """ Change the value of the vars """
                self.coffee_left_threshold = float(
                    settings[settings["name"] == "coffee_left_threshold"]["value"])
                self.coffee_ordered = self.check_bool(
                    settings[settings["name"] == "coffee_ordered"]["value"])
                self.coffee_notification_ordered = self.check_bool(
                    settings[settings["name"] == "coffee_notification_ordered"]["value"])
                self.coffee_notification_empty = self.check_bool(
                    settings[settings["name"] == "coffee_notification_empty"]["value"])
                self.delivery_time = int(settings[settings["name"] == "delivery_time"]["value"])
                self.mail_supplier = []
                self.mail_supplier.append(settings[settings["name"] == "mail_supplier"]["value"].iloc[0])
                self.mail_message = settings[settings["name"] == "mail_message"]["value"].iloc[0]
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

    def get_coffee_settings(self):
        try:
            data = {}
            data["coffee_left_threshold"] = self.coffee_left_threshold/1000
            data["delivery_time"] = self.delivery_time
            data["mail_supplier"] = self.mail_supplier[0]
            data["mail_message"] = self.mail_message.replace('<br>', '\n')
            return data
        except Exception as ex:
            logging.error(ex)
            raise ex
