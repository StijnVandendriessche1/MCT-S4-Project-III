""" Class for the comment to a topic """
import logging
import argparse
import io
import os
import sys
import time
import json
from google.api_core.exceptions import AlreadyExists
from google.cloud import iot_v1
from google.cloud import pubsub
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.errors import HttpError
import sys, os
import jsonpickle

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/cert.json'

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class PubSubComment:
    def __init__(self, id):
        # TODO:Aan StijnVandendriessche1 vragen
        """For setting up the object.

        Args:
            id ([type]): [description]
        """        
        try:
            self.registry_id="OfficeOfTheFuture"
            self.cloud_region="europe-west1"
            self.project_id="engaged-context-277613"
            self.device_id=id
            self.service_account_json="/home/pi/cert.json"
        except Exception as e:
            logging.error(e)
    
    def send_message(self, message):
        """This fucntion sends a message to a device

        Args:
            message (string/json): This must be a message

        Raises:
            e: Error-message

        Returns:
            [type]: [description]
        """        
        try:
            """Send a command to a device."""
            # [START iot_send_command]
            print('Sending command to device')
            client = iot_v1.DeviceManagerClient()
            device_path = client.device_path(self.project_id, self.cloud_region, self.registry_id, self.device_id)
            data = message.encode('utf-8')
            return client.send_command_to_device(device_path, data)
        except Exception as e:
            logging.error(e)
            raise e