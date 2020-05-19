import sys, os
from datetime import datetime
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.data import Data

class Sensordata:
    def __init__(self, measurement, host, data = []):
        self.measurement = measurement
        self.host = host
        self.data = data