from threading import Thread
import logging

from queue import Queue
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.sensordata import Sensordata
from Models.data import Data
from Logic.influxdb import Influxdb
from Models.MeetingBox import MeetingBox
from time import sleep

""" Class for the room-ai """
logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


class MeetingBoxSystem:
    def __init__(self, meetingbox_queue):
        try:
            self.status_ai = True
            self.meetingbox_queue = meetingbox_queue
            self.influxdb = Influxdb("Pi")
            self.meetingboxes = self.initialize_meetingboxes()
            self.start()
        except Exception as e:
            logging.error(e)

    def start(self):
        """This is the mean-function. It starts the all functions that are needed for the MeetingBoxSystem

        Raises:
            ex: Error-message
        """
        try:
            self.get_meeting_box_status()
            self.get_count_persons()

            """ Start check-thread + start the thread"""
            t_check_meeting_box_status = Thread(
                target=self.check_meetingboxes_status)
            t_check_meeting_box_status.start()
        except Exception as ex:
            logging.error(ex)
            raise ex

    def initialize_meetingboxes(self):
        """Create a list with objects of MeetingBox

        Raises:
            ex: Error

        Returns:
            List: This function returns a list of MeetingBox objects
        """
        try:
            meetingboxes = []
            meetingboxes.append(MeetingBox("GoldenEye"))
            meetingboxes.append(MeetingBox("Casino Royale"))
            meetingboxes.append(MeetingBox("Moon Raker"))
            meetingboxes.append(MeetingBox("Gold Finger"))
            return meetingboxes
        except Exception as ex:
            logging.error(ex)
            raise ex

    def get_meeting_box_status(self):
        """This function gets the status of each meetingbox from the influxdb

        Raises:
            Exception: Error-message
        """
        try:
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "meetingbox_status") |> filter(fn: (r) => r["host"] == "webserver") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> unique(column: "meetingbox")'
            settings_data = self.influxdb.get_data(query, False)
            if settings_data.empty:
                # TODO --> Change it to the class MeetingBox
                for meetingbox, status in self.status_meeting_box.items():
                    self.change_status_influxdb(
                        "meetingbox", "meetingbox_status", meetingbox, self.status_meeting_box[meetingbox])
            else:
                for i, meetingbox in enumerate(self.meetingboxes):
                    row = settings_data[settings_data["meetingbox"]
                                        == meetingbox.name]
                    self.meetingboxes[i].buzzy = bool(
                        row["status"].astype(bool).values[0])
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def get_count_persons(self):
        """This function gets the number of persons in each meetingbox from the Influxdb

        Raises:
            ex: Error-message
        """
        try:
            query = ''' |> range(start: 2018-05-22T23:30:00Z)
                        |> filter(fn: (r) => r["_measurement"] == "sensordata")
                        |> filter(fn: (r) => r["_field"] == "persons")
                        |> last()
                        |> unique(column:"host")'''
            settings_data = self.influxdb.get_data(query, False)
            if not settings_data.empty:
                """ Set the person_count into the list of meetingboxes """
                for i, meetingbox in enumerate(self.meetingboxes):
                    try:
                        row = settings_data[settings_data["host"]
                                            == meetingbox.name]
                        self.meetingboxes[i].buzzy = int(
                            row["_value"].astype(int).values[0])
                    except:
                        pass
        except Exception as ex:
            logging.error(ex)
            raise ex

    def check_meetingboxes_status(self):
        """
        This function get the new count of persons from the Influxdb 
        """
        try:
            if self.status_ai:
                self.get_count_persons()
                for i, meetingbox in enumerate(self.meetingboxes):
                    """ Check if the meetingbox is changed """
                    if meetingbox.last_change == 0 and meetingbox.persons > 0:
                        self.meetingboxes[i].last_change = meetingbox.persons
                        self.meetingboxes[i].buzzy = True
                        self.meetingbox_queue.put(0)
                    elif meetingbox.last_change > 0 and meetingbox.last_change == 0:
                        self.meetingboxes[i].last_change = meetingbox.persons
                        self.meetingboxes[i].buzzy = False
                        self.meetingbox_queue.put(0)
            sleep(61)
        except Exception as ex:
            logging.error(ex)

    def change_meeting_box(self, box):
        """Function that can be call when the user will change the meeting box status with the toggle-switch

        Args:
            box (MeetingBox): This var must be an object of MeetingBox

        Raises:
            Exception: Error-message

        Returns:
            dict: This function returns a dictionary
        """        
        # Function that can be call when the user will change the meeting box status with the toggle-switch
        try:
            """ Find the object in the list """
            meetingbox = [mb for mb in self.meetingboxes if mb.name == box]
            if len(meetingbox)==1:
                i = self.meetingboxes.index(meetingbox[0])
                if self.meetingboxes[i]:
                    self.meetingboxes[i] = False
                else:
                    self.meetingboxes[i] = True
                self.change_to_influxdb(self.meetingboxes[i].name, self.meetingboxes[i].buzzy)
            return self.get_status()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_to_influxdb(self, meetingbox):
        """This function sends the changes to the Google Pub/Sub

        Args:
            meetingbox (MeetingBox): This var must be an object of MeetingBox

        Raises:
            ex: Error-message
        """
        try:
            data = []
            data.append(Data("status", meetingbox.buzzy))
            data.append(Data("meetingbox", meetingbox.name))
            sensordata = Sensordata("meetingbox_status", self.host, data)
            # TODO --> Send it to the Google Pub/Sub
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def get_status(self):
        """This function returns the current status

        Raises:
            ex: Error-message

        Returns:
            dict: Returns a dict with key: name of the meetingbox and value: the current status of the meetingbox
        """
        try:
            meetingboxes_dict = {}
            for meetingbox in self.meetingboxes:
                meetingboxes_dict[meetingbox.name] = meetingbox.buzzy
            return meetingboxes_dict
        except Exception as ex:
            logging.error(ex)
            raise ex

test_queue = Queue()
test = MeetingBoxSystem(test_queue)
test.change_meeting_box("GoldenEye")