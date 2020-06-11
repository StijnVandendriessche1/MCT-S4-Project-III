""" Class for coffee """
import sys
import os
import logging

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.send_mail import SendMail

logging.basicConfig(filename="piKeuken/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


class Coffee:
    def __init__(self, notification_queue):
        self.coffee_left = 0
        self.coffee_left_order = 3000
        self.coffee_ordered = False
        self.coffee_notification_ordered = False
        self.coffee_notification_empty = False
        self.notification_queue = notification_queue
        self.send_mail = SendMail()
        self.mail_coffee_company = ["tibo.van.craenenbroeck@student.howest.be"]

    def coffee_checker(self, coffee_left):
        try:
            """ Change the coffee_left """
            self.coffee_left = coffee_left
            """ Check if the coffee must be ordered """
            if self.coffee_left <= self.coffee_left_order and self.coffee_notification_ordered == False:
                """ Send a notification """
                self.send_mail.send_message(
                    "Bestelling koffie ML6", "Beste<br><br>Graag zouden wij 20Kg koffie bestellen bij jullie.<br><br>MVG<br>ML6", self.mail_coffee_company)
                self.coffee_notification_ordered = True
                self.notification_queue.put(
                    {"name": "☕", "message": "🚚 Your coffee is on it's way! 🚚"})
            elif self.coffee_left >= 11 and self.coffee_notification_empty == False:
                self.notification_queue.put(
                    {"name": "☕", "message": "😥 Oh no! Coffee is finished, Time for starbucks 🚶‍♀️"})
                self.coffee_notification_empty = True
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
