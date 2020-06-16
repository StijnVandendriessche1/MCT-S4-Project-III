import logging
from datetime import datetime, timedelta

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.influxdb import Influxdb

""" Class for the dishwasher """

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


class Dishwasher:
    def __init__(self):
        try:
            # TODO --> Load the notification_queue
            # TODO --> Implement a database for the settings
            # TODO --> Change the settings
            self.hour_notification = timedelta(hours=16, minutes=0)
            self.vibration_intensity = 9000
            self.status = False
            self.hour_on = datetime.now()
            self.duration = datetime.timedelta(minutes=3600)
        except Exception as e:
            logging.error(e)

    def start(self):
        try:
            """ Create a thread that checks if the dishwasher is on and if de server must send a notification """
        except Exception as e:
            logging.error(e)

    def check_state(self):
        try:
            """ Check if the dishwasher is on """
            if self.status == False:
                pass
            elif self.status and (self.hour_on + self.duration) >= datetime.now():
                """ Check if the dishwasher is done """
                self.status = False
                # TODO --> Send a notification
        except Exception as e:
            logging.error(e)
            raise e

    def check_vibration(self):
        try:
            """ Check if the dishwasher is on --> Get the last 3 rows """
            # TODO --> Get the last 3 rows from the database
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "sensor_data") |> filter(fn: (r) => r["host"] == "kitchen") |> filter(fn: (r) => r["_value"] == "dishwasher") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") last()'
            settings_data = self.influxdb.get_data(query, False)
            if not settings_data.empty:
                pass
        except Exception as e:
            logging.error(e)

    def check_hour(self):
        try:
            if datetime.now() >= self.hour_notification:
                """ Query for getting the last row """
                query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "sensor_data") |> filter(fn: (r) => r["host"] == "kitchen") |> filter(fn: (r) => r["_value"] == "dishwasher") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") last()'
                settings_data = self.influxdb.get_data(query, False)
                if not settings_data.empty:
                    """ Send a notification """
                    pass
        except Exception as e:
            logging.error(e)
            raise e