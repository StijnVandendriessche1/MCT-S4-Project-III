""" Class for send to the mqtt-server
pip install paho-mqtt """

import jsonpickle

from queue import Queue
from threading import Thread

import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import json

import sys
import os
import logging

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars

class MQTT:
    def __init__(self, topic, pubsub=False, messages_queue=None):
        try:
            self.pubsub = pubsub
            self.messages_queue = messages_queue
            self.get_vars = GetVars()
            self.ip = self.get_vars.get_var("MQTT_IP")
            self.port = self.get_vars.get_var("MQTT_Port")
            self.topic = topic
            self.qos = 1
            self.start()
        except Exception as ex:
            raise Exception(ex)

    def start(self):
        try:
            self.Client = mqtt.Client()
            if self.pubsub:
                self.Client.on_connect = self.on_connect
                self.Client.on_message = self.on_message
                self.Client.on_disconnect = self.on_disconnect
                self.Client.on_publish = self.on_publish

            self.Client.connect(self.ip, self.port, 60)

            if self.pubsub:
                self.Client.loop_forever()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def on_connect(self, client, userdata, flags, rc):
        try:
            self.Client.subscribe(self.topic)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def on_message(self, client, userdata, msg):
        try:
            message = jsonpickle.decode(msg.payload)
            self.messages_queue.put(message)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def on_disconnect(self, client, userdata, rc):
        print("hier")
    
    def on_publish(self, client, userdata, mid):
        print(client)

    def publish(self, data):
        try:
            print("b", self.Client.is_connected())
            json_data = jsonpickle.encode(data)
            self.Client.publish(self.topic, payload=json_data,
                                qos=self.qos, retain=False)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    


""" test = MQTT("test")
test_json = {"test": "Topi"}
test.publish(test_json) """

""" messages_queue = Queue()

def start_mqtt():
    test = MQTT("test", True, messages_queue)

def send_data():
    message = messages_queue.get()
    while True:
        print(message)
        messages_queue.task_done()
        message = messages_queue.get()


t = Thread(target=start_mqtt)
t.start()

t = Thread(target=send_data)
t.start() """
