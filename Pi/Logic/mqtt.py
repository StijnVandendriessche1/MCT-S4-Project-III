""" Class for send to the mqtt-server
pip install paho-mqtt """


import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import json

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars


class MQTT:
    def __init__(self, topic):
        self.get_vars = GetVars()
        self.ip = self.get_vars.get_var("MQTT_IP")
        self.port = self.get_vars.get_var("MQTT_Port")
        self.topic = topic
        self.qos = 1
        self.start()

    def start(self):
        self.Client = mqtt.Client()
        self.Client.on_connect = self.on_connect
        self.Client.on_message = self.on_message

        self.Client.connect(self.ip, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        self.Client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        pass

    def publish(self, data):
        objPayload = json.dumps(data)
        self.Client.publish(self.topic, payload=objPayload,
                            qos=self.qos, retain=False)


test = MQTT("test")
test_json = {"test": "Topi"}
test.publish(test_json)
