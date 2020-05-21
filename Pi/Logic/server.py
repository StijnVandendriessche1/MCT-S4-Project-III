import logging
import sys, os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.influxdb import Influxdb
from Logic.get_vars import GetVars

""" Class for the main_server"""
class Server:
    def __init__(self):
        try:
            self.host = "MainServer"
            self.influxdb_settings = Influxdb("Pi")
            self.influxdb_sensors = Influxdb("Pi")
            self.influxdb_cloud = Influxdb("Cloud")
            self.start_status()
        except Exception as ex:
            logging.error(ex)
    
    def start_status(self):
        try:
            self.status_ai = {
                "ai_meeting": False,
                "ai_coffee": False,
                "ai_dishwasher": False
            }
            self.get_ai_status()
        except Exception as ex:
            raise Exception(ex)
    
    def get_ai_status(self):
        try:
            settings_data = self.influxdb_settings.get_data('|> range(start:-111h)')
            if settings_data == []:
                for ai, status in self.status_ai.items():
                    self.change_ai_status_influxdb(ai, status)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_ai_status_influxdb(self, ai, status):
        self.influxdb_cloud.write_data_to_influxdb(ai, self.host, "status", status)
    
    def change_ai_status(self, ai):
        try:
            if self.status_ai[ai]:
                self.status_ai[ai] = False
            else:
                self.status_ai[ai] = True
            self.change_ai_status_influxdb(ai, self.status_ai[ai])
            return self.get_ai_status
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)