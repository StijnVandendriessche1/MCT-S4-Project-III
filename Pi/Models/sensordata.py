import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.data import Data


class Sensordata:
    def __init__(self, measurement, host, data=[], timestamp = int(time.time()*1000000000)):
        self.measurement = measurement
        self.host = host
        self.timestamp = timestamp
        self.data = data
    
    def __eq__(self, other):
        return self.host == other.host and self.measurement == other.measurement and self.timestamp == other.timestamp