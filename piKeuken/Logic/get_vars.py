import sys
import os
import json
import logging
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s    %(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class GetVars:
    def __init__(self):
        """ /home/pi/project3/settings.json 
            piKeuken\settings.json"""
        self.file = f"{BASE_DIR}/settings.json"
        self.vars = self.start()

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
