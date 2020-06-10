import sys
import os
import json
import logging
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

logging.basicConfig(filename="piKeuken/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class GetVars:
    def __init__(self):
        try:
            """ /home/pi/project3/settings.json """
            self.file = "piKeuken\settings.json"
            self.vars = self.start()
        except Exception as ex:
            logging.error(ex)

    def start(self):
        try:
            with open(self.file, "r") as f:
                my_dict = json.load(f)
            return my_dict
        except Exception as ex:
            logging.error(ex)
            raise ex

    def get_var(self, name):
        try:
            return self.vars[name]
        except Exception as ex:
            logging.error(ex)
            raise ex
