import sys
import os
import json
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)


class GetVars:
    def __init__(self):
        self.file = "../settings.json"
        self.vars = self.start()

    def start(self):
        with open(self.file, "r") as f:
            my_dict = json.load(f)
        return my_dict

    def get_var(self, name):
        return self.vars[name]


""" test = GetVars()
print(test.get_var("InfluxDB_Token")) """
