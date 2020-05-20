""" Class for write the data to the InfluxDB 2.O (cloud) """


from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.data import Data
from Models.sensordata import Sensordata
from Logic.get_vars import GetVars

class Influxdb:
    def __init__(self, host="", read = False):
        self.get_vars = GetVars()
        self.host = host
        self.connection = False
        self.Messages = []
        if read:
            self.token = self.get_vars.get_var("InfluxDB_Token_Read")
        else:
            self.token = self.get_vars.get_var("InfluxDB_Token_Write")
        self.start()

    def start(self):
        try:
            self.org = self.get_vars.get_var("Org")
            self.bucket = self.get_vars.get_var("Bucket")
            self.client = InfluxDBClient(
                url=self.get_vars.get_var("InfluxDB_URL"), token=self.token)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.connection = True
        except Exception as ex:
            print(ex)

    def write_data(self, sensordata):
        try:
            for data in sensordata.data:
                sequence = [
                    f"{sensordata.measurement},host={sensordata.host} {data.key}={data.value}"]
                self.write_api.write(self.bucket, self.org, sequence)
            return True
        except Exception as ex:
            print(ex)
            return False

    """ def get_messages(self):
         """

    def get_data(self, query_in):
        query = f'from(bucket: "{self.bucket}") {query_in}'
        tables = self.client.query_api().query(query, org=self.org)
        results = []
        for table in tables:
            for record in table.records:
                results.append([record.get_value(), record.get_field()])
        return results

""" test = Influxdb('Kitchen', True)
a = test.get_data('|> range(start: -24h) |> filter(fn: (r) => r["_measurement"] == "temperature_room")')
print(a) """

""" test = Influxdb("Kitchen")
print(test.write_data("temperature_room", "temperature", 21.31)) """
