""" Class for coffee """
import sys
import os
import logging

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.send_mail import SendMail

class Coffee:
    def __init__(self):
        self.coffee_left = 0.0
        self.coffee_left_order = 3.0
        self.coffee_ordered = False
        self.days_without_coffee = 0
        self.send_mail = SendMail()

    def coffee_checker(self):
        try:
            """ Check if the coffee must be ordered """
            if self.coffee_left <= self.coffee_left_order and self.coffee_ordered == False:
                """ Send a mail to the dealer """
                self.coffee_ordered = True
                """ DIT NOG AANPASSEN!!! """
                self.send_mail.send_message(
                    message_from, message_subject, message_body, message_to=[])
            elif self.coffee_left == 0.0 and self.coffee_ordered:
                self.days_without_coffee += 1
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
