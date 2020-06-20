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


logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")
                    
class SendMail:
    def __init__(self):
        """Makes a API-connection for sending mails
        """        
        try:
            self.getvars = GetVars()
            self.sg = SendGridAPIClient(self.getvars.get_var("SendGrid_key"))
        except Exception as ex:
            logging.error(ex)
    
    def send_message(self, message_subject, message_body, message_to = [], message_from = "tibo.van.craenebroeck@ext.ml6.eu"):
        """This fcuntoin sends a mail to the persons that are in the list

        Args:
            message_subject (string): This is the subject of the mail mail
            message_body (string): This is the body of the mail
            message_to (list, optional): This is a list of string (with the addresses of the persons to send). Defaults to [].
            message_from (str, optional): This must be the email address from who it is sent. Defaults to "tibo.van.craenebroeck@ext.ml6.eu".

        Raises:
            Exception: Error-message with the exception

        Returns:
            int: It returns the status code
        """        
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