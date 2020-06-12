from Sensors.Mcp import Mcp
import RPi
from RPi import GPIO
from Sensors.dht11 import DHT11
from Sensors.klasseknop import Button
import time
import threading
import datetime
import time
import jwt
import paho.mqtt.client as mqtt
from Models.data import Data
from Models.sensordata import Sensordata
import jsonpickle
from Logic.mqtt_pub_sub import MQTT
import queue
from Logic.switch import Button
import pandas as pd
import numpy as np
GPIO.setmode(GPIO.BCM)

run = True

light = 0
temp = 0
hmdt = 0
pvaat = 0
vaat = 0
prs = {'person': 0}

mcp = Mcp(0,0)
dht = DHT11(pin=17)
q = queue.Queue()
mqtt = MQTT(2817465839732274, q)
vibr = Button(pin=27)
door = Button(pin=2)

def run_light():
    global light
    while run:
        light = 100 - (mcp.read_channel(1) / 1024 * 100)

def run_temp():
    global temp
    while run:
        temp = mcp.read_channel(0) / 1024 * 330

def run_hmdt():
    global hmdt
    while run:
        result = dht.read()
        if result.is_valid():
            hmdt = result.humidity

def tril_vaat(a):
    print("trilling gedetecteerd")
    t = []
    t.append(Data("dishwasherstate", "Detect").__dict__)
    x = Sensordata("sensordata", "Kitchen", t)
    y = jsonpickle.encode(x.__dict__)
    mqtt.send(y)
    print(y)


def door_change(a):
    doorstate = door.pressed
    data = np.array([doorstate])
    ser = pd.Series(data)
    doorstate = ser.map({True: 'closed', False: 'open'})
    doorstate = str(doorstate.values[0])
    t = []
    t.append(Data("doorstate", doorstate).__dict__)
    x = Sensordata("sensordata", "Kitchen", t)
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
    vibr.on_change(tril_vaat)
    door.on_change(door_change)
    door_change(0)
    #actPrs = threading.Thread(target=run_human_count)
    #actPrs.start()
    #actQueueListener = threading.Thread(target=queue_listener)
    #actQueueListener.start()

    while True:
        t = []
        t.append(Data("temperature", temp).__dict__)
        t.append(Data("light", light).__dict__)
        t.append(Data("humidity", hmdt).__dict__)
        x = Sensordata("sensordata", "Kitchen", t)
        y = jsonpickle.encode(x.__dict__)
        mqtt.send(y)
        print(y)
        time.sleep(5)

except KeyboardInterrupt as ex:
    try:
        print("Shutting down...")
        run = False
        time.sleep(10)
        GPIO.cleanup()
        print("goodbye")
    except Exception as e:
        print(e)
        run = False
        time.sleep(10)
        GPIO.cleanup()
        print("goodbye")
except Exception as ex:
    print("something went wrong")
    run = False
    time.sleep(10)
    GPIO.cleanup()
    print("goodbye")