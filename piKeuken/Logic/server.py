from queue import Queue
import random

import logging
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Models.data import Data
from Models.sensordata import Sensordata
from Logic.influxdb import Influxdb
from Logic.get_vars import GetVars
from Logic.notifications import Notifications
from Logic.coffee import Coffee
from Logic.dishwasher import Dishwasher
from Logic.meeting_boxes import MeetingBoxSystem


""" Class for the main_server"""

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

class Server:
    def __init__(self):
        try:
            self.host = "webserver"
            self.influxdb = Influxdb("Pi")
            self.influxdb_cloud = Influxdb("Cloud")
            self.notifications = Notifications()
            self.coffee = Coffee(self.notifications.new_notifications_queue)
            self.dishwasher = Dishwasher(self.notifications.new_notifications_queue)
            self.meetingbox = MeetingBoxSystem()
            self.threshold_light = 71.0
            self.start_status()
        except Exception as ex:
            logging.error(ex)

    def start_status(self):
        """Starts the webserver

        Raises:
            Exception: Error-message
        """        
        try:
            self.status_ai = {
                "ai_meeting": False,
                "ai_coffee": False,
                "ai_dishwasher": False
            }
            self.get_ai_status()
            """ Change the ai_status in the systems """
            self.coffee.ai_status = self.status_ai["ai_coffee"]
            self.dishwasher.ai_status = self.status_ai["ai_dishwasher"]
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def get_ai_status(self):
        """Get the ai-status of each system.

        Raises:
            Exception: Error-message
        """
        try:
            query = '|> range(start: 2018-05-22T23:30:00Z) |> filter(fn: (r) => r["_measurement"] == "ai_status") |> filter(fn: (r) => r["host"] == "webserver") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") |> unique(column: "ai")'
            settings_data = self.influxdb.get_data(query, False)
            if settings_data.empty:
                for ai, status in self.status_ai.items():
                    self.change_status_influxdb("ai", "ai_status", ai, status)
            else:
                for ai in self.status_ai:
                    row = settings_data[settings_data["ai"] == ai]
                    status_ai = bool(row["status"].astype(bool).values[0])
                    self.status_ai[ai] = status_ai
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_status_influxdb(self,sort,sort_status, key, status):
        try:
            data = []
            data.append(Data("status", status))
            data.append(Data(sort, key))
            sensordata = Sensordata(sort_status, self.host, data)
            self.influxdb_cloud.write_data(sensordata)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def change_ai_status(self, ai):
        """This function changes the ai-status from the frontend and get the new status from the Influxdb

        Args:
            ai (string): This string must be the name of the system

        Raises:
            Exception: Error-message
        """        
        try:
            if self.status_ai[ai]:
                self.status_ai[ai] = False
            else:
                self.status_ai[ai] = True
            self.change_status_influxdb("ai", "ai_status", ai, self.status_ai[ai])
            """ Change the ai_status in the systems """
            self.coffee.ai_status = self.status_ai["ai_coffee"]
            self.dishwasher.ai_status = self.status_ai["ai_dishwasher"]
            self.get_ai_status()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def check_coffee_status(self):
        """This function gets the last sensordata from the coffee from the Influxdb

        Raises:
            Exception: Error-message

        Returns:
            float: This function returns a value with 2 decimal places
        """        
        try:
            query = ''' |> range(start: 2018-05-22T23:30:00Z)
                        |> last()
                        |> filter(fn: (r) => r["_measurement"] == "sensordata")
                        |> filter(fn: (r) => r["_field"] == "weight")'''
            coffee_status = self.influxdb.get_data(query)
            if coffee_status.empty == False:
                """ Change the coffee_left_status + check if there is enough """
                self.coffee.coffee_checker(coffee_status["weight"][0])
            return round((self.coffee.coffee_left/1000), 2)
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)

    def check_status_dishwasher(self):
        """This function returns the status of the dishwasher

        Raises:
            Exception: Error-message

        Returns:
            bool: This function returns a True by on and a False by off.
        """        
        try:
            return self.dishwasher.get_dishwasher_status()
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    
    def get_info_box(self, box):
        """This function gets the last info about the rooms (temp, humidity, light)

        Args:
            box (string): This string must be the name of the room

        Raises:
            Exception: Error-message

        Returns:
            JSON: This function returns a json object
        """        
        try:
            box = box.replace(" ", "_")
            query = f'|> range(start: 2018-05-22T23:30:00Z) |> last() |> filter(fn: (r) => r["_measurement"] == "sensordata") |> filter(fn: (r) => r["host"] == "{box}") |> sort(columns: ["_time"], desc: true) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
            data_info = self.influxdb.get_data(query, False)
            for i, r in enumerate(data_info):
                for col in data_info.columns:
                    try:
                        data_info[col] = data_info[col].fillna(data_info.iloc[i][col])
                    except:
                        pass
            return data_info.to_json(orient="records")
        except Exception as ex:
            logging.error(ex)
            raise Exception(ex)
    
    def get_notifications(self, user_info):
        try:
            notifications_result = self.notifications.get_notifications(user_info["id"])
            notifications_result["viewed"] = [False if uid else True for uid in notifications_result["uid"].isnull()]
            notifications_result = notifications_result.drop(columns=["uid"])
            return notifications_result.to_dict(orient="records")
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def get_day_of_week(self, day):
        """This function returns the day of the week

        Args:
            day (int): This must be a number between 0 and 7.

        Returns:
            string: This function returns the day of the week in string format
        """
        if day == 0:
            return "Sunday"
        elif day == 1:
            return "Monday"
        elif  day == 3:
            return "Tuesday"
        elif  day == 4:
            return "Wednesday"
        elif day == 5:
            return "Thursday"
        elif day == 6:
            return "Friday"
        elif  day == 7:
            return "Saturday"
        return "Unknown"
    
    def get_coffee_day_of_week(self):
        """This function gets the mean coffee_left_weight of each DayOfWeek and returns it in JSON. (For the graph on the dashboard)

        Raises:
            ex: Error-Message

        Returns:
            JSON: This function returns a json object
        """        
        try:
            query ="""  |> range(start: 2018-05-22T23:30:00Z)
                        |> filter(fn: (r) => r["host"] == "Coffee")
                        |> filter(fn: (r) => r["_field"] == "weight")
                        |> map(fn: (r) => ({ r with "DayOfWeek": date.weekDay(t: r["_time"])}))
                        |> group(columns:["DayOfWeek"])
                        |> mean(column: "_value")
                        """
            coffee_data = self.influxdb.get_data(query, False, 'import "date"')
            #""" Add a week name to the dataframe """
            coffee_data["WeekDay"] = [self.get_day_of_week(day) for day in coffee_data["DayOfWeek"]]
            return coffee_data.to_json(orient="records")
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def get_temperature_by_room(self):
        """This function gets the mean temperature of each room from the Influxdb (for the graph on the dashboard)

        Raises:
            ex: Error-message

        Returns:
            JSON: This function returns a JSON object
        """        
        try:
            query ="""  |> range(start: 2018-05-22T23:30:00Z)
                        |> filter(fn: (r) => r["_measurement"] == "sensordata")
                        |> filter(fn: (r) => r["_field"] == "temperature")
                        |> mean(column: "_value")
                        """
            temperature = self.influxdb.get_data(query, False)
            return temperature.to_json(orient="records")
        except Exception as ex:
            logging.error(ex)
            raise ex
    
    def get_humidity_by_room(self):
        """This function gets the mean humidity of each room from the influxdb (for the graph on the dashboard)

        Raises:
            ex: Error-message

        Returns:
            JSON: This function returns a JSON object
        """        
        try:
            query ="""  |> range(start: 2018-05-22T23:30:00Z)
                        |> filter(fn: (r) => r["_measurement"] == "sensordata")
                        |> filter(fn: (r) => r["_field"] == "humidity")
                        |> mean(column: "_value")
                        """
            temperature = self.influxdb.get_data(query, False)
            return temperature.to_json(orient="records")
        except Exception as ex:
            logging.error(ex)
            raise ex
    

    def get_light(self):
        """This function gets the last status of the light of every room

        Raises:
            ex: Error-message

        Returns:
            dict: This returns a dictionary with keys: room and value: light-status (true or false)
        """        
        try:
            query = '|> range(start: 2018-05-22T23:30:00Z) |> last() |> filter(fn: (r) => r["_measurement"] == "sensordata") |> filter(fn: (r)=>r["_field"]=="light") |> sort(columns: ["_time"], desc: true)'
            light = self.influxdb.get_data(query, False)
            """ Check if the light is higher than the threshold """
            light_rooms = {}
            for i, light_room in light.iterrows():
                try:
                    if light_room["_value"]>=self.threshold_light:
                        light_rooms[light_room["host"]]=True
                    else:
                        light_rooms[light_room["host"]]=False
                except:
                    pass
            return light_rooms
        except Exception as ex:
            logging.error(ex)
            raise ex