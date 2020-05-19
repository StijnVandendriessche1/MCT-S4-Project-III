""" Class for write the data to the InfluxDB 2.O (cloud) """

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class Influxdb:
    def __init__(self, host):
        self.host = host
        self.connection = False
        self.start()

    def start(self):
        try:
            token = "0FYRJRMjyVbUZo-0Aln-7oN37v_5VzW1Abpv_ERUAABivBZ1hji1oOtcVmiVsP6LqdUCFRo_hcJpECg_k2Z8mA=="
            self.org = "6a7311f79ed1ac39"
            self.bucket = "robin.deneef's Bucket"
            client = InfluxDBClient(
                url="https://us-central1-1.gcp.cloud2.influxdata.com", token=token)
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
