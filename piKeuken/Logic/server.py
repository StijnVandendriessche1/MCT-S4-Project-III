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
from Logic.notifications import Notifications
from Logic.coffee import Coffee


""" Class for the main_server"""

logging.basicConfig(filename="piKeuken/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class Server:
    def __init__(self):
        try:
            self.host = "webserver"
            self.influxdb = Influxdb("Pi")
            self.influxdb_cloud = Influxdb("Cloud")
            self.notifications = Notifications()
            self.coffee = Coffee(self.notifications.new_notifications_queue)
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
                "GoldenEye": False,
                "Casino Royale": False,
                "Moon Raker": False,
                "Gold Finger": False
            }
            self.get_ai_status()
            self.get_meeting_box_status()
        except Exception as ex:
            raise Exception(ex)

    def get_ai_status(self):
        try:
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "ai_status") |> filter(fn: (r) => r["host"] == "webserver") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> unique(column: "ai")'
            settings_data = self.influxdb.get_data(query, False)
            if settings_data.empty:
                for ai, status in self.status_ai.items():
                    self.change_ai_status_influxdb(ai, status)
            else:
                for ai in self.status_ai:
                    row = settings_data[settings_data["ai"] == ai]
                    status_ai = bool(row["status"].astype(bool).values[0])
                    self.status_ai[ai] = status_ai
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_status_influxdb(self,sort,sort_status, key, status):
        try:
            data = []
            data.append(Data("status", status))
            data.append(Data(sort, key))
            sensordata = Sensordata(sort_status, self.host, data)
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
            self.change_status_influxdb("ai", "ai_status", ai, self.status_ai[ai])
            return self.get_ai_status
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def check_coffee_status(self):
        try:
            query = ''' |> range(start: 2018-05-22T23:30:00Z)
                        |> last()
                        |> filter(fn: (r) => r["_measurement"] == "sensordata")
                        |> filter(fn: (r) => r["_field"] == "weight")'''
            coffee_status = self.influxdb.get_data(query)
            if coffee_status.empty == False:
                """ Change the coffee_left_status + check if there is enough """
                self.coffee.coffee_checker(coffee_status["weight"][0])
            return self.coffee.coffee_left
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
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "meetingbox_status") |> filter(fn: (r) => r["host"] == "webserver") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> unique(column: "meetingbox")'
            settings_data = self.influxdb.get_data(query, False)
            if settings_data.empty:
                for meetingbox, status in self.status_meeting_box.items():
                    self.change_status_influxdb("meetingbox", "meetingbox_status", meetingbox, self.status_meeting_box[meetingbox])
            else:
                for status_meetingbox in self.status_meeting_box:
                    row = settings_data[settings_data["meetingbox"] == status_meetingbox]
                    status_meeting_box = bool(row["status"].astype(bool).values[0])
                    self.status_meeting_box[status_meetingbox] = status_meeting_box
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_meeting_boxs(self, box):
        try:
            if self.status_meeting_box[box]:
                self.status_meeting_box[box] = False
            else:
                self.status_meeting_box[box] = True
            self.change_status_influxdb("meetingbox", "meetingbox_status", box, self.status_meeting_box[box])
            return self.status_meeting_box
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    
    def get_info_box(self, box):
        try:
            query = f'|> range(start: 2018-05-22T23:30:00Z) |> last() |> filter(fn: (r) => r["_measurement"] == "sensordata") |> filter(fn: (r) => r["host"] == "{box}") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
            data_info = self.influxdb.get_data(query, False)
            return data_info.to_json(orient="records")
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)