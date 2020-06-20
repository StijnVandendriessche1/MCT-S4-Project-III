#!/usr/bin/python
import datetime
import time
import jwt
import logging
import paho.mqtt.client as mqtt
import jsonpickle
import sys, os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars
#from Logic.AutoDeployGit import AutoDeployGit
from Logic.influxdb import Influxdb

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s    %(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class MQTT:
    def __init__(self, device_id, queue = None):
        """The init is for setup the settings

        Args:
            device_id (int): This must be the id of the device (from the Google IOT Core)
            queue (Queue, optional): This must be a Queue. Defaults to None.
        """        
        try:
            self.get_vars = GetVars()
            self.influxdb = Influxdb()
            self.queue = queue
            self.runPrs = False
            self.runCoffee = False
            self.runDish = False
            self.isUpdating = False
            self.get_ai_status()
            self.ssl_algorithm = self.get_vars.get_var("GoogleIOT_Algorithm") # Either RS256 or ES256
            self.ssl_private_key_filepath = self.get_vars.get_var("GoogleIOT_PrivateKey")
            self.root_cert_filepath = self.get_vars.get_var("GoogleIOT_CertPath")
            self.project_id = self.get_vars.get_var("GoogleIOT_ProjectID")
            self.gcp_location = self.get_vars.get_var("GoogleIOT_Location")
            self.registry_id = self.get_vars.get_var("GoogleIOT_RegistryId")
            self.device_id = device_id
            self._CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(self.project_id, self.gcp_location, self.registry_id, self.device_id)
            self.topic = '/devices/{}/events'.format(self.device_id)
            self.commandTopic = '/devices/{}/commands/#'.format(self.device_id)
            self.client = mqtt.Client(client_id=self._CLIENT_ID)
            self.start()

        except Exception as ex:
            logging.error(ex)

    def start(self):
        """This function is for starting everything

        Raises:
            Exception: Error-message of the exception
        """        
        try:
            # authorization is handled purely with JWT, no user/pass, so username can be whatever
            self.client.username_pw_set(
                username='unused',
                password=self.create_jwt())

            self.client.on_connect = self.on_connect
            self.client.on_publish = self.on_publish
            self.client.on_message = self.on_message

            self.client.tls_set(ca_certs=self.root_cert_filepath) # Replace this with 3rd party cert if that was used when creating registry
            self.client.connect('mqtt.googleapis.com', 8883)
            self.client.loop_start()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def create_jwt(self):
        """This function is for creating a JWT token for the connection with the Google IOT-Core

        Raises:
            Exception: Error-message

        Returns:
            [type]: [description]
        """        
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
        """Runs this function if the device is connected with Google. Set a subscribe on a topic with QOS 1.
        """        
        print('on_connect', self.error_str(rc))
        self.client.subscribe(self.commandTopic, qos=1)

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Run this function when a publish is successful
        """        
        print('on_publish')

    def on_message(self, unused_client, unused_userdata, message):
        """Run this function when a message is received

        Arg:
            message (object): This is the message that must be decoded to utf-8
        """        
        try:
            payload = str(message.payload.decode('utf-8'))
            print(payload)
            command = jsonpickle.loads(payload)
            keys = command.keys()
            k = ""
            for key in keys:
                k = key
                break
            value = command[k]
            if k == "people":
                if value == "off":
                    self.runPrs = False
                    print("people counter stopped")
                elif value == "on":
                    self.runPrs = True
                    self.queue.put("people")
                    print("people counter started")
                else:
                    print("command not recognised")
            elif k == "dishwasher_ai":
                if value == "off":
                    self.runDish = False
                    print("dishwasher_ai stopped")
                elif value == "on":
                    self.runDish = True
                    print("dishwasher_ai started")
                else:
                    print("command not recognised")
            elif k == "coffee":
                if value == "off":
                    self.runCoffee = False
                    print("coffee_ai stopped")
                elif value == "on":
                    self.runCoffee = True
                    print("coffee_ai started")
                else:
                    print("command not recognised")
            elif k == "update":
                if not self.isUpdating:
                    self.isUpdating = True
                    print("starting update...")
                    os.system('sudo rm -rf /home/pi/MCT-S4-Project-III/')
                    os.system('sudo git clone https://github.com/StijnVandendriessche1/MCT-S4-Project-III.git /home/pi/MCT-S4-Project-III')
                    os.system('sudo rm -rf /home/pi/project3/*')
                    os.system('cp -r /home/pi/MCT-S4-Project-III/piKeuken/. /home/pi/project3/')
                    os.system('cp /home/pi/settings.json /home/pi/project3')
                    print("updated")
                    os.system('sudo shutdown -r')
                    self.queue.put("quit")

        except Exception as ex:
            logging.error(ex)
            print("failed to execute command")


    def send(self, payload):
        try:
            self.client.publish(self.topic, payload, qos=1)
            time.sleep(1)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    
    def get_ai_status_from_df(self, settings_data, ai):
        """This function gets the ai_status from the dataframe and returns

        Args:
            settings_data (DataFrame): This must be a dataframe
            ai (string): This must be the name of the system

        Returns:
            bool: This function returns true if on and false if the system is off
        """
        try:
            row = settings_data[settings_data["ai"] == ai]
            return bool(row["status"].astype(bool).values[0])
        except:
            return False
    
    def get_ai_status(self):
        """Set the ai_status of the system.

        Raises:
            Exception: Error-message
        """
        try:
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "ai_status") |> filter(fn: (r) => r["host"] == "webserver") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> unique(column: "ai")'
            settings_data = self.influxdb.get_data(query, False)
            if not settings_data.empty:
                self.runPrs = self.get_ai_status_from_df(settings_data, "ai_meeting")
                self.runCoffee = self.get_ai_status_from_df(settings_data, "ai_coffee")
                self.runDish = self.get_ai_status_from_df(settings_data, "ai_dishwasher")
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)