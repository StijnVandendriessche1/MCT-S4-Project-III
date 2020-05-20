from time import sleep

import random
import logging
import sys
import os

from datetime import datetime
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars
from Logic.mqtt import MQTT
from Models.data import Data
from Models.sensordata import Sensordata


logging.basicConfig(filename="Logging.txt", level=logging.INFO, format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


class PiKitchen:
    def __init__(self):
        try:
            self.get_vars = GetVars()
            self.host = "Kitchen"
            self.mqtt = MQTT(self.get_vars.get_var("Topic"))
            self.start()
        except Exception as ex:
            logging.error(ex)

    def start(self):
        while True:
            try:
                data = []
                data.append(Data("temperature", self.temperature_sensor()))
                sensordata = Sensordata(
                    "temperature_room", self.host, datetime.now(), data)
                self.mqtt.publish(sensordata)
                sleep(3)
            except Exception as ex:
                logging.info(ex)
                raise Exception(ex)

    def temperature_sensor(self):
        try:
            temperature = random.uniform(-1.1, 31.1)
            return temperature
        except Exception as ex:
            logging.info(ex)
            raise Exception(ex)


start = PiKitchen()
