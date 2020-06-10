""" Class for sending mails """
import sendgrid
import logging

logging.basicConfig(filename="piKeuken/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")
                    
class SendMail:
    def __init(self):
        try:
            self.sg = sendgrid.SendGridClient("YOUR_SENDGRID_API_KEY")
        except Exception as ex:
            logging.error(ex)
    
    def send_message(self, message_from, message_subject, message_body, message_to = []):
        try:
            message = sendgrid.Mail()

            message.add_to()
            message.set_from(message_from)
            message.set_subject(message_subject)
            message.set_html(message_body)
            self.sg.send(message)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)


