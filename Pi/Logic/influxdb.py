""" Class for write the data to the InfluxDB 2.O (cloud) """

from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
import sys
import os


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars

class Influxdb:
    def __init__(self, host):
        self.get_vars = GetVars()
        self.host = host
        self.connection = False
        self.start()

    def start(self):
        try:
            token = self.get_vars.get_var("InfluxDB_Token")
            self.org = self.get_vars.get_var("Org")
            self.bucket = self.get_vars.get_var("Bucket")
            client = InfluxDBClient(
                url=self.get_vars.get_var("InfluxDB_URL"), token=token)
            self.write_api = client.write_api(write_options=SYNCHRONOUS)
            self.connection = True
        except Exception as ex:
            print(ex)

    def write_data(self, measurement, key, value):
        try:
            sequence = [f"{measurement},host={self.host} {key}={value}"]
            self.write_api.write(self.bucket, self.org, sequence)
            return True
        except Exception as ex:
            print(ex)
            return False


""" test = Influxdb("Kitchen")
print(test.write_data("temperature_room", "temperature", 21.31)) """
