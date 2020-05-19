import sys
import os
from queue import Queue
from threading import Thread

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.influxdb import Influxdb
from Logic.mqtt import MQTT


class TestSRV:
    def __init__(self):
        self.messages_queue = Queue()
        self.start()
    
    def start(self):
        t_mqtt = Thread(target=self.start_mqtt)
        t_mqtt.start()

        t_get_data = Thread(target=self.get_data)
        t_get_data.start()

    def start_mqtt(self):
        test = MQTT("test", True, self.messages_queue)

    def get_data(self):
        message = self.messages_queue.get()
        while True:
            print(message)
            self.messages_queue.task_done()
            message = self.messages_queue.get()


start = TestSRV()
