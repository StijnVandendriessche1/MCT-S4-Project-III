import sys, os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.data import Data

class Sensordata:
    def __init__(self, measurement, data = []):
        self.measurement = measurement
        self.data = data
