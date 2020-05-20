import sys
import os
from datetime import datetime, timezone
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.data import Data


class Sensordata:
    def __init__(self, measurement, host, datetime, data=[]):
        self.measurement = measurement
        self.host = host
        self.datetime = datetime
        self.data = data

    @property
    def datetime(self):
        return self.__datetime

    @datetime.setter
    def datetime(self, value):
        try:
            #datetime_timestamp = value.timestamp()
            """ datetime_string = value.strftime('%Y-%m-%d %H:%M:%S')
            datetime_string += '.' + str(int(datetime_timestamp % 1000000000)).zfill(9) """
            #datetime_string = value.strftime('%Y-%m-%dT%H:%M:%SZ')
            #datetime_string = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            #datetime_string = str(datetime.utcnow())
            #datetime_string = str(value) + "000000000"
            datetime_timestamp = datetime.now().timestamp()*1000
            self.__datetime = datetime_timestamp
        except Exception as ex:
            print(ex)
