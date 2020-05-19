""" Class for send to the mqtt-server
pip install paho-mqtt """

from queue import Queue
from threading import Thread

import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import json

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars
import jsonpickle


class MQTT:
    def __init__(self, topic, pubsub=False, messages_queue = None):
        self.pubsub = pubsub
        self.messages_queue = messages_queue
        self.get_vars = GetVars()
        self.ip = self.get_vars.get_var("MQTT_IP")
        self.port = self.get_vars.get_var("MQTT_Port")
        self.topic = topic
        self.qos = 1
        self.start()

    def start(self):
        self.Client = mqtt.Client()
        if self.pubsub:
            self.Client.on_connect = self.on_connect
            self.Client.on_message = self.on_message

        self.Client.connect(self.ip, self.port, 60)

        if self.pubsub:
            self.Client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.Client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        #message = json.loads(msg.payload)
        message = jsonpickle.decode(msg.payload)
        self.messages_queue.put(message)

    def publish(self, data):
        json_data = jsonpickle.encode(data)
        #objPayload = json.dumps(json_data)
        self.Client.publish(self.topic, payload=json_data,
                            qos=self.qos, retain=False)


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