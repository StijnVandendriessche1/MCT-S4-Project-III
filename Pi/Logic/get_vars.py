import sys
import os
import json
import logging
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)


class GetVars:
    def __init__(self):
        try:
            self.file = "Pi\settings.json"
            self.vars = self.start()
        except Exception as ex:
            raise Exception(ex)

    def start(self):
        try:
            with open(self.file, "r") as f:
                my_dict = json.load(f)
            return my_dict
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def get_var(self, name):
        try:
            return self.vars[name]
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)


""" test = GetVars()
print(test.get_var("InfluxDB_Token")) """
