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
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

class PubSubComment:
    def __init__(self):
        try:
            self.registry_id="enmregistry"
            self.cloud_region="europe-west1"
            self.project_id="iotcoredemo-send"
            self.device_id="pidieter"
            self.service_account_json="creds.json"
        except Exception as e:
            logging.error(e)
    
    def send_message(self,message):
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