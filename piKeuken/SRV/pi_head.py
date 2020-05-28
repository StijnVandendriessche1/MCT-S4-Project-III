import sys
import os
from queue import Queue
from threading import Thread

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.influxdb import Influxdb
from Logic.mqtt import MQTT
from Logic.get_vars import GetVars

from Models.sensordata import Sensordata
from Models.data import Data
import logging

logging.basicConfig(filename="Logging.txt", level=logging.INFO, format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


class PiHead:
    def __init__(self):
        try:
            self.get_vars = GetVars()
            self.messages_queue = Queue()
            self.influxdb = Influxdb()
            self.start()
        except Exception as ex:
            logging.error(ex)
    
    def start(self):
        try:
            t_mqtt = Thread(target=self.start_mqtt)
            t_mqtt.start()

            t_get_data = Thread(target=self.get_data)
            t_get_data.start()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def start_mqtt(self):
        try:
            mqtt = MQTT(self.get_vars.get_var("Topic"), True, self.messages_queue)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def get_data(self):
        try:
            message = self.messages_queue.get()
            while True:
                try:
                    self.influxdb.write_data(message)
                    self.messages_queue.task_done()
                    message = self.messages_queue.get()
                except Exception as ex:
                    logging.error(ex)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)


start = PiHead()
