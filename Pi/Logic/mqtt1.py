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

import argparse
import datetime
import os
import random
import ssl
import time
import jwt

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)
from Logic.get_vars import GetVars
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


class MQTT:
    def __init__(self, client_id, username, topic, pubsub=False, messages_queue=None):
        try:
            self.client_id = client_id
            self.username = username
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

    def init(self):
        # The initial backoff time after a disconnection occurs, in seconds.
        self.minimum_backoff_time = 1

        # The maximum backoff time before giving up, in seconds.
        self.MAXIMUM_BACKOFF_TIME = 32

        # Whether to wait with exponential backoff before publishing.
        self.should_backoff = False

    def jwt(self, project_id, private_key_file, algorithm):
        try:
            token = {
                # The time that the token was issued at
                'iat': datetime.datetime.utcnow(),
                # The time the token expires.
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                # The audience field should always be set to the GCP project id.
                'aud': project_id
            }

            # Read the private key file.
            with open(private_key_file, 'r') as f:
                private_key = f.read()

            return jwt.encode(token, private_key, algorithm=algorithm)
        except Exception as ex:
            logging.Error(ex)
            raise Exception(ex)

    def start(self):
        try:
            self.init()
            self.Client = mqtt.Client(client_id=self.client_id)
            pwd = self.jwt(self.get_vars.get_var("GoogleIOT_ProjectID"), self.get_vars.get_var(
                "GoogleIOT_PrivateKey"), self.get_vars.get_var("GoogleIOT_Algorithm"))
            self.client.username_pw_set(username=self.username,password=pwd)
            # Enable SSL/TLS support.
            self.client.tls_set(ca_certs=self.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

            if self.pubsub:
                self.Client.on_connect = self.on_connect
                self.Client.on_message = self.on_message
                self.Client.on_disconnect = self.on_disconnect
                self.Client.on_publish = self.on_publish

            #self.Client.connect(self.ip, self.port, 60)
            # Connect to the Google MQTT bridge.
            self.client.connect(self.mqtt_bridge_hostname, self.mqtt_bridge_port)

            if self.pubsub:
                self.Client.loop_forever()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    def parse_command_line_args(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description=(
                'Example Google Cloud IoT Core MQTT device connection code.'))
        parser.add_argument(
                '--algorithm',
                choices=('RS256', 'ES256'),
                required=True,
                help='Which encryption algorithm to use to generate the JWT.')
        parser.add_argument(
                '--ca_certs',
                default='roots.pem',
                help='CA root from https://pki.google.com/roots.pem')
        parser.add_argument(
                '--cloud_region', default='us-central1', help='GCP cloud region')
        parser.add_argument(
                '--data',
                default='Hello there',
                help='The telemetry data sent on behalf of a device')
        parser.add_argument(
                '--device_id', required=True, help='Cloud IoT Core device id')
        parser.add_argument(
                '--gateway_id', required=False, help='Gateway identifier.')
        parser.add_argument(
                '--jwt_expires_minutes',
                default=20,
                type=int,
                help='Expiration time, in minutes, for JWT tokens.')
        parser.add_argument(
                '--listen_dur',
                default=60,
                type=int,
                help='Duration (seconds) to listen for configuration messages')
        parser.add_argument(
                '--message_type',
                choices=('event', 'state'),
                default='event',
                help=('Indicates whether the message to be published is a '
                    'telemetry event or a device state message.'))
        parser.add_argument(
                '--mqtt_bridge_hostname',
                default='mqtt.googleapis.com',
                help='MQTT bridge hostname.')
        parser.add_argument(
                '--mqtt_bridge_port',
                choices=(8883, 443),
                default=8883,
                type=int,
                help='MQTT bridge port.')
        parser.add_argument(
                '--num_messages',
                type=int,
                default=100,
                help='Number of messages to publish.')
        parser.add_argument(
                '--private_key_file',
                required=True,
                help='Path to private key file.')
        parser.add_argument(
                '--project_id',
                default=os.environ.get('GOOGLE_CLOUD_PROJECT'),
                help='GCP cloud project name')
        parser.add_argument(
                '--registry_id', required=True, help='Cloud IoT Core registry id')
        parser.add_argument(
                '--service_account_json',
                default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
                help='Path to service account json file.')

        # Command subparser
        command = parser.add_subparsers(dest='command')

        command.add_parser(
            'device_demo',
            help=mqtt_device_demo.__doc__)

        command.add_parser(
            'gateway_send',
            help=send_data_from_bound_device.__doc__)

        command.add_parser(
            'gateway_listen',
            help=listen_for_messages.__doc__)

        self.args = parser.parse_args()
    

    def on_connect(self, client, userdata, flags, rc):
        try:
            self.should_backoff = False
            self.minimum_backoff_time = 1
            self.Client.subscribe(self.topic, qos=1)
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
        print("Disconnected")
        self.should_backoff = True

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
