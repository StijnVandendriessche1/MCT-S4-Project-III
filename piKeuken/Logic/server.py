from queue import Queue
import random

import logging
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.data import Data
from Models.sensordata import Sensordata
from Logic.influxdb import Influxdb
from Logic.get_vars import GetVars

""" Class for the main_server"""


class Server:
    def __init__(self):
        try:
            self.host = "webserver"
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
            self.status_meeting_box = {
                "Meeting Box 1": True,
                "Meeting Box 2": False,
                "Meeting Room": False,
                "Big Meeting Room": True
            }
            self.get_ai_status()
            self.get_meeting_box_status()
        except Exception as ex:
            raise Exception(ex)

    def get_ai_status(self):
        try:
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "ai_status") |> filter(fn: (r) => r["host"] == "webserver") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> unique(column: "ai")'
            settings_data = self.influxdb_settings.get_data(query, False)
            if settings_data.empty:
                for ai, status in self.status_ai.items():
                    self.change_ai_status_influxdb(ai, status)
            else:
                for ai in self.status_ai:
                    row = settings_data[settings_data["ai"] == ai]
                    test = row["status"]
                    print(test)
                    print(ai, row)
                    #self.status_ai[ai] = settings_data[]
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_ai_status_influxdb(self, ai, status):
        try:
            data = []
            data.append(Data("status", status))
            data.append(Data("ai", ai))
            sensordata = Sensordata("ai_status", self.host, data)
            self.influxdb_cloud.write_data(sensordata)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

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

    def check_coffee_status(self):
        try:
            return round(random.uniform(11, 31), 1)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def check_status_dishwasher(self):
        try:
            random_status = [True, False]
            return random.choice(random_status)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def get_meeting_box_status(self):
        try:
            return self.status_meeting_box
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_meeting_boxs(self, box):
        try:
            if self.status_meeting_box[box]:
                self.status_meeting_box[box] = False
            else:
                self.status_meeting_box[box] = True
            return self.status_meeting_box
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
