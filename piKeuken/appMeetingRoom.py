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
from Logic.ml_object_detection import MLObjectDetection
import queue
import cv2

GPIO.setmode(GPIO.BCM)

run = True

light = 0
temp = 0
hmdt = 0
prs = {'person': 0}

mcp = Mcp(0,0)
dht = DHT11(pin=17)
ml = MLObjectDetection()
q = queue.Queue()
mqtt = MQTT(3052736401110405, q)
startPrs = False


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

def run_human_count():
    global prs
    global startPrs
    global ml
    while run:
        if mqtt.runPrs:
            if startPrs:
                ml = MLObjectDetection()
                startPrs = False
            prs = ml.count_total_objects
        else:
            if startPrs == False:
                ml.stop()
                del ml
                startPrs = True

    #global prs
    #ml.cap = cv2.VideoCapture(0)
    #counter_objects = threading.Thread(target=ml.count_objects)
    #counter_objects.start()
    #while run and mqtt.runPrs:
        #prs = ml.count_total_objects
    #ml.stop()

def queue_listener():
    global actPrs
    while run:
        com = q.get()
        if com == "people":
            mqtt.runPrs = True
            del actPrs
            actPrs = threading.Thread(target=run_human_count)
            actPrs.start()
            #actPrsCount = threading.Thread(target=run_human_count)
            #actPrsCount.start()
            q.task_done()
        else:
            print("command not found")

try:
    actLight = threading.Thread(target=run_light)
    actLight.start()
    actTemp = threading.Thread(target=run_temp)
    actTemp.start()
    actHmdt = threading.Thread(target=run_hmdt)
    actHmdt.start()
    actPrs = threading.Thread(target=run_human_count)
    actPrs.start()
    actQueueListener = threading.Thread(target=queue_listener)
    actQueueListener.start()



    while True:
        #print("light: %f%%" % light)
        #print("temperature: %f°C" % temp)
        #print("humidity: %d%%" % hmdt)
        #print(str(prs.get('person')))
        #print("")
        t = []
        t.append(Data("temperature", temp))
        t.append(Data("light", light))
        t.append(Data("humidity", hmdt))
        if mqtt.runPrs:
            t.append(Data("persons", prs.get('person')))
        x = Sensordata("sensordata", "MeetingRoom", t)
        #print(x.timestamp)
        y = jsonpickle.encode(x)
        mqtt.send(y)
        print(y)
        time.sleep(5)

except Exception as ex:
    print(ex)
    ml.cleanup()
    run = False
    time.sleep(1)
    GPIO.cleanup()
    print("goodbye")