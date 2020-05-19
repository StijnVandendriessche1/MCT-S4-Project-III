import random

import sys, os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.sensordata import Sensordata
from Models.data import Data

from Logic.mqtt import MQTT
from Logic.get_vars import GetVars

from time import sleep

class PiKitchen:
    def __init__(self):
        self.get_vars = GetVars()
        self.host = "Kitchen"
        self.mqtt = MQTT(self.get_vars.get_var("Topic"))
        self.start()
    

    def start(self):
        while True:
            try:
                data = []
                data.append(Data("temperature", self.temperature_sensor()))
                sensordata = Sensordata("temperature_room",self.host, data)
                self.mqtt.publish(sensordata)
                sleep(3)
            except Exception as ex:
                print(ex)

    def temperature_sensor(self):
        try:
            temperature = random.uniform(-1.1, 31.1)
            return temperature
        except Exception as ex:
            print(ex)


start = PiKitchen()