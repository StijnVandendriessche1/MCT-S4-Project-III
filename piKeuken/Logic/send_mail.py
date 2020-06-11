""" Class for sending mails """
import logging

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import sys
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars


logging.basicConfig(filename="piKeuken/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")
                    
class SendMail:
    def __init__(self):
        try:
            self.getvars = GetVars()
            self.sg = SendGridAPIClient(self.getvars.get_var("SendGrid_key"))
        except Exception as ex:
            logging.error(ex)
    
    def send_message(self, message_subject, message_body, message_to = [], message_from = "tibo.van.craenebroeck@ext.ml6.eu"):
        try:
            message = Mail(
            from_email=message_from,
            to_emails=message_to,
            subject=message_subject,
            html_content=message_body)
            response = self.sg.send(message)
            return response.status_code
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)