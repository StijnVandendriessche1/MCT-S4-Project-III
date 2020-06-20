""" Class for write the data to the InfluxDB 2.O (cloud) """


import pandas as pd
import logging

from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WritePrecision, Dialect

from datetime import datetime
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars
from Models.sensordata import Sensordata
from Models.data import Data

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s    %(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class Influxdb:
    def __init__(self, token_type="Pi"):
        """This is the init. Het setup the influxdb-connection

        Args:
            token_type (str, optional): Use Pi for reads, Cloud for reads/writes. Defaults to "Pi".
        """        
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
        """Get the settings from the settings.json-file and start a write-api

        Raises:
            Exception: Error-message
        """        
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
        """This function makes a string from the data that must be insert in the influxdb

        Args:
            sensordata (list): This must be a list of Sensordata (data)

        Returns:
            bool: It returns true if successful
        """        
        try:
            fields = ""
            for i, data in enumerate(sensordata.data):
                """ Check if the value is a string """
                if isinstance(data.value, str):
                    data.value = f'"{data.value}"'
                """ Put the keys and values in a string """
                if i != 0:
                    fields += f",{data.key}={data.value}"
                else:
                    fields = f"{data.key}={data.value}"
            """ Put the row into the database """
            self.write_data_to_influxdb(
                sensordata.measurement, sensordata.host, fields, sensordata.timestamp)
            return True
        except Exception as ex:
            logging.error(ex)
            return False

    def write_data_to_influxdb(self, measurement, host, fields, timestamp):
        """This function is for writing data to the InfluxDB. It can only works with a cloud-object (This class with token_type=cloud)

        Args:
            measurement (string): This must be the measurement
            host (string): This must be the host
            fields (string): This must be the data that should be written
            timestamp (int): This must be in nanoseconds (bug in influxdb 2.0)

        Raises:
            ex: Error-message
        """                
        try:
            """ Convert the datatime to a timestamp in nanoseconds """
            #timestamp = int(datetime.timestamp()*1000000000)
            sequence = [f"{measurement},host={host} {fields} {timestamp}"]
            """ Push it into the influxDB cloud """
            self.write_api.write(self.bucket, self.org, sequence)
        except Exception as ex:
            logging.error(ex)
            raise ex

    def get_data(self, query_in, change_format=True, in_import = ""):
        """This function can be called by a pi or cloud token-type-object. It returns a dataframe

        Args:
            query_in (string): This must be the query that wil execute
            change_format (bool, optional): If the _field must be the column name and the _value must be the value, set this to true. Defaults to True.
            in_import (str, optional): If there are imports needed (example: date). Defaults to "".

        Raises:
            Exception: Error-message

        Returns:
            [type]: Dataframe
        """        
        try:
            if change_format:
                query_in += ' |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
            query = f'{in_import} from(bucket: "{self.bucket}") {query_in}'
            results = self.client.query_api().query_data_frame(query, org=self.org)
            """ Set _ to space """
            if "host" in results.columns:
                results["host"] = [host.replace("_", " ") for host in results["host"]]
            return results
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
