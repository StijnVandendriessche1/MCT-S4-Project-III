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
import logging
import pandas as pd

class Influxdb:
    def __init__(self, token_type = "Pi"):
        try:
            self.get_vars = GetVars()
            self.connection = False
            self.Messages = []
            """ check which device it is """
            if token_type == "Pi":
                self.token = self.get_vars.get_var("InfluxDB_Token_Pi")
            else:
                self.token = self.get_vars.get_var("InfluxDB_Token_Cloud")
            self.start()
        except Exception as ex:
            logging.error(ex)

    def start(self):
        try:
            self.bucket = self.get_vars.get_var("Bucket")
            self.org = self.get_vars.get_var("Org")
            self.client = InfluxDBClient(
                url=self.get_vars.get_var("InfluxDB_URL"), token=self.token)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.connection = True
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def write_data(self, sensordata):
        try:
            fields = ""
            for i, data in enumerate(sensordata.data):
                """ Check if the value is a string """
                if isinstance(data.value, str):
                    data.value = f'"{data.value}"'
                """ Put the keys and values in a string """
                if i!=0:
                    fields += f",{data.key}={data.value}"
                else:
                    fields = f"{data.key}={data.value}"
            """ Put the row into the database """
            self.write_data_to_influxdb(sensordata.measurement, sensordata.host, fields, sensordata.timestamp)
            return True
        except Exception as ex:
            logging.error(ex)
            return False
    
    def write_data_to_influxdb(self, measurement, host, fields, timestamp):
        try:
            """ Convert the datatime to a timestamp in nanoseconds """
            #timestamp = int(datetime.timestamp()*1000000000)
            sequence = [f"{measurement},host={host} {fields} {timestamp}"]
            """ Push it into the influxDB cloud """
            self.write_api.write(self.bucket, self.org, sequence)
        except Exception as ex:
            logging.error(ex)
            raise ex

    def get_data(self, query_in):
        try:
            query = f'from(bucket: "{self.bucket}") {query_in}'
            #results = self.client.query_api().query_stream(query, org=self.org)
            #results = self.client.query_api().query_data_frame(query, org=self.org)
            tables = self.client.query_api().query(query, org=self.org)
            """ test = pd.DataFrame(tables)
            print(test.head(5))
            print(test[0][0]) """
            results = []
            for index, table in enumerate(tables):
                result_row = []
                for record in table.records:
                    result_row.append([record.get_field(), record.get_value()])
            return results
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

""" test = Influxdb('Kitchen', True)
a = test.get_data('|> range(start: -24h) |> filter(fn: (r) => r["_measurement"] == "temperature_room")')
print(a) """

""" test = Influxdb("sensors", "Kitchen", "Pi")
a = test.get_data('|> range(start:-111h)')
print(a) """

""" testa = Influxdb("Cloud")
data = []
data.append(Data("status", False))
data.append(Data("ai", "meeting"))
sensordata = Sensordata("Jos", "TestServer", data)
print(testa.write_data(sensordata))


test = Influxdb("Pi")
a = test.get_data('|> range(start:-111h) |> filter(fn: (r) => r["_measurement"] == "Jos")') """

#print(a)