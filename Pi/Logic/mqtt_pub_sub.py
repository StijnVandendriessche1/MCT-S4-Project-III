#!/usr/bin/python
import datetime
import time
import jwt
import logging
import paho.mqtt.client as mqtt

import sys, os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars

class MQTT:
    def __init__(self, device_id):
        try:
            self.get_vars = GetVars()

            self.ssl_algorithm = self.get_vars.get_var("GoogleIOT_Algorithm") # Either RS256 or ES256
            self.ssl_private_key_filepath = self.get_vars.get_var("GoogleIOT_PrivateKey")
            self.root_cert_filepath = self.get_vars.get_var("GoogleIOT_CertPath")
            self.project_id = self.get_vars.get_var("GoogleIOT_ProjectID")
            self.gcp_location = self.get_vars.get_var("GoogleIOT_Location")
            self.registry_id = self.get_vars.get_var("GoogleIOT_RegistryId")
            self.device_id = device_id
            self._CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(self.project_id, self.gcp_location, self.registry_id, self.device_id)
            self.topic = '/devices/{}/events'.format(self.device_id)
            self.client = mqtt.Client(client_id=self._CLIENT_ID)
            self.start()

        except Exception as ex:
            logging.error(ex)
    
    def start(self):
        try:
            #self.client = mqtt.Client(client_id=self._CLIENT_ID)
            # authorization is handled purely with JWT, no user/pass, so username can be whatever
            self.client.username_pw_set(
                username='unused',
                password=self.create_jwt())
            
            self.client.on_connect = self.on_connect
            self.client.on_publish = self.on_publish

            self.client.tls_set(ca_certs=self.root_cert_filepath) # Replace this with 3rd party cert if that was used when creating registry
            self.client.connect('mqtt.googleapis.com', 8883)
            #self.client.loop_start()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    
    def create_jwt(self):
        try:
            cur_time = datetime.datetime.utcnow()
            token = {
                'iat': cur_time,
                'exp': cur_time + datetime.timedelta(minutes=60),
                'aud': self.project_id
            }

            with open(self.ssl_private_key_filepath, 'r') as f:
                private_key = f.read()

            return jwt.encode(token, private_key, self.ssl_algorithm)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    
    def error_str(self, rc):
        return '{}: {}'.format(rc, mqtt.error_string(rc))

    def on_connect(self, unusued_client, unused_userdata, unused_flags, rc):
        print('on_connect', self.error_str(rc))

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        print('on_publish')
    
    def send(self, payload):
        try:
            """ #payload = '{{ "ts": {}, "temperature": {}, "pressure": {}, "humidity": {} }}'.format(int(time.time()), temperature, light, humidity)
            payload = "hallo" """

            self.client.publish(self.topic, payload, qos=1)
            time.sleep(1)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    
#test = MQTT("DEVICEID")
