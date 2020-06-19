from Sensors.Mcp import Mcp
#import RPi
from RPi import GPIO
from Sensors.dht11 import DHT11
from Sensors.klasseknop import Button
import time
import threading
import datetime
import time
import jwt
import paho.mqtt.client as mqtt
import jsonpickle
from Logic.mqtt_pub_sub import MQTT
from Logic.ml_object_detection import MLObjectDetection
import queue
from Models.sensordata import Sensordata
from Models.data import Data
import cv2
from Logic.switch import Button
import pandas as pd
import numpy as np
import json
GPIO.setmode(GPIO.BCM)

run = True

light = 0
temp = 0
hmdt = 0
prs = {'person': 0}

mcp = Mcp(0,0)
dht = DHT11(pin=17)
q = queue.Queue()
mqtt = MQTT(3052736401110405, q)
door = Button(27)

def run_light():
    global light
    while run:
        light = 100 - (mcp.read_channel(1) / 1024 * 100)
    print("light stopped")

def run_temp():
    global temp
    while run:
        temp = mcp.read_channel(0) / 1024 * 330
    print("temperatuur stopped")

def run_hmdt():
    global hmdt
    while run:
        result = dht.read()
        if result.is_valid():
            hmdt = result.humidity
    print("humidity stopped")

def run_human_count():
    global prs
    ml = MLObjectDetection()
    while mqtt.runPrs and run:
        prs = ml.count_total_objects
        time.sleep(3)
    ml.stop()
    del ml
    print("personcounter stopped")

def queue_listener():
    global actPrs
    global run
    while run:
        com = q.get()
        if com == "people":
            actPrs = threading.Thread(target=run_human_count)
            actPrs.start()
            q.task_done()
        elif com == "quit":
            run = False
            time.sleep(5)
            break
        else:
            print("command not found")
    print("queuelistener stopped")

def door_change(a):
    doorstate = door.pressed
    data = np.array([doorstate])
    ser = pd.Series(data)
    doorstate = ser.map({True: 'closed', False: 'open'})
    doorstate = str(doorstate.values[0])
    t = []
    t.append(Data("doorstate", doorstate).__dict__)
    x = Sensordata("sensordata", "GoldenEye", t)
    y = jsonpickle.encode(x.__dict__)
    mqtt.send(y)
    print(y)

try:
    actLight = threading.Thread(target=run_light)
    actLight.start()
    actTemp = threading.Thread(target=run_temp)
    actTemp.start()
    actHmdt = threading.Thread(target=run_hmdt)
    actHmdt.start()
    actQueueListener = threading.Thread(target=queue_listener)
    actQueueListener.start()
    door.on_change(door_change)
    door_change(0)

    while run:
        t = []
        t.append(Data("temperature", temp).__dict__)
        t.append(Data("light", light).__dict__)
        t.append(Data("humidity", hmdt).__dict__)
        if mqtt.runPrs:
            t.append(Data("persons", prs.get('person')).__dict__)
        x = Sensordata("sensordata", "GoldenEye", t)
        y = jsonpickle.encode(x.__dict__)
        mqtt.send(y)
        print(y)
        time.sleep(5)
    q.put("quit")
    GPIO.cleanup()
    print("goodbye")

except KeyboardInterrupt as ex:
    print("Shutting down...")
except Exception as ex:
    print("something went wrong")
    print(ex)
finally:
    run = False
    time.sleep(5)
    q.put("quit")
    GPIO.cleanup()
    print("goodbye")

#als je dit leest dan werkt de deployment