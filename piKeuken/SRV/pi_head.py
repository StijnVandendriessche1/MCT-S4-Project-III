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


class PiHead:
    def __init__(self):
        self.get_vars = GetVars()
        self.messages_queue = Queue()
        self.influxdb = Influxdb()
        self.start()
    
    def start(self):
        t_mqtt = Thread(target=self.start_mqtt)
        t_mqtt.start()

        t_get_data = Thread(target=self.get_data)
        t_get_data.start()

    def start_mqtt(self):
        test = MQTT(self.get_vars.get_var("Topic"), True, self.messages_queue)

    def get_data(self):
        message = self.messages_queue.get()
        while True:
            try:
                self.influxdb.write_data(message)
                self.messages_queue.task_done()
                message = self.messages_queue.get()
            except Exception as ex:
                print(ex)


start = PiHead()
