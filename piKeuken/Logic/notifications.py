""" Class for notifications """
from time import sleep
import threading
from queue import Queue
import logging
import uuid

import sys
import os
from threading import Thread
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.db import DB
from datetime import datetime

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s    %(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class Notifications:
    def __init__(self):
        """Init of the object
        """        
        try:
            self.notification_queue = Queue()
            self.new_notifications_queue = Queue()
            self.db = DB()
            self.start()
        except Exception as ex:
            logging.error(ex)
    
    def start(self):
        """Start a thread that gets the new notifications from the system.

        Raises:
            ex: Error-message with the exception
        """        
        try:
            t_new_notifications = Thread(target=self.new_notification_queue)
            t_new_notifications.start()
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def new_notification_queue(self):
        """This function gets the new notifications from the system (queue) and send it to the new_notification-function

        Raises:
            ex: Error-message
        """        
        try:
            while True:
                new_notification = self.new_notifications_queue.get()
                self.new_notification(new_notification["name"], new_notification["message"])
                self.new_notifications_queue.task_done()
        except Exception as ex:
            logging.error(ex)
            raise ex

    def new_notification(self, name, message):
        """This function gets the new notification and put it into the SQLite database

        Args:
            name (string): This must be the name of the notification
            message (string): This must be the message of the notification

        Raises:
            ex: Error-message with the exception
        """        
        try:
            #""" Put the notification in the database """
            id = str(uuid.uuid4().hex)
            self.db.execute(
                "INSERT INTO tb_notifications(id, name, message, datetime) VALUES (?, ?, ?, ?)", (id, name, message, datetime.now()))
            #""" Send it to the frontend """
            self.notification_queue.put({"name": name, "message": message})
        except Exception as ex:
            logging.error(ex)
            raise ex

    def notification_viewed(self, notification_id, user_id):
        """This function must be called when a user viewed a notification

        Args:
            notification_id (string): This must be the id of the notification
            user_id (int): This must be the id of the user (Google Auth)

        Raises:
            ex: Error-message with the exception
        """        
        try:
            #""" Check if the notification exists """
            notification_exist = self.db.execute(
                "SELECT COUNT(id) as amount FROM tb_notifications WHERE id=:NotificationId", {"NotificationId": notification_id}, True)
            if notification_exist.iloc[0]["amount"] == 1:
                #""" Check if the user already has the viewed the notification"""
                notification_viewed = self.db.execute(
                    "SELECT COUNT(user_id) as amount FROM tb_notifications_viewed WHERE notification_id=:NotificationId AND user_id=:UserId", {"NotificationId": notification_id, "UserId": user_id}, True)
                if notification_viewed.iloc[0]["amount"] == 0:
                    #""" Add the user with the notification into the database """
                    self.db.execute(
                        "INSERT INTO tb_notifications_viewed(notification_id, user_id) VALUES(:NotificationId,:UserId)", {"NotificationId": notification_id, "UserId": user_id})
        except Exception as ex:
            logging.error(ex)
            raise ex

    def get_notifications(self, user_id):
        """This function gets all the notifications from a user

        Args:
            user_id (int): User-id (Google Auth)

        Raises:
            ex: Error-message with the exception

        Returns:
            dataframe: It returns a dataframe with all the notifications from the user
        """        
        try:
            #""" Get the notifications from the database """
            notifications = self.db.execute('''SELECT id as nid, name as title, message as msg, user_id as uid, tb_notifications.datetime as dt FROM tb_notifications
                                            LEFT JOIN tb_notifications_viewed
                                            ON tb_notifications_viewed.notification_id= tb_notifications.id
                                            AND tb_notifications_viewed.user_id=:UserId
                                            ORDER BY dt DESC''', {'UserId':user_id}, True)
            return notifications
        except Exception as ex:
            logging.error(ex)
            raise ex
