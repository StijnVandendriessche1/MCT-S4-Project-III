""" Class for notifications """
import logging

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.db import DB

class Notifications:
    def __init__(self):
        try:
            self.db = DB()
        except Exception as ex:
            logging.error(ex)
    
    def new_notification(self, name, message):
        try:
            pass
        except Exception as ex:
            logging.error(ex)
            raise ex
