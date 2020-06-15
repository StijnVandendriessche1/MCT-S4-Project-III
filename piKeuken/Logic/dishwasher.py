from datetime import datetime

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.influxdb import Influxdb
import logging

""" Class for the dishwasher """

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class Dishwasher:
    def __init__(self):
        self.check_hour = "16:00"

    def check_state(self):
        if datetime.strptime(self.check_hour, '%H:%M').time() == datetime.now().time():
            """ Query for getting the last row """
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "sensor_data") |> filter(fn: (r) => r["host"] == "kitchen") |> filter(fn: (r) => r["_value"] == "dishwasher") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") last()'
            settings_data = self.influxdb.get_data(query, False)
            if not settings_data.empty:
                """ Send a notification """
                pass
""" TODO --> Wanneer hij 2 of 3 keer de threshold overschreid --> Dan staat hij aan """

""" test = Dishwasher()
test.check_state() """
