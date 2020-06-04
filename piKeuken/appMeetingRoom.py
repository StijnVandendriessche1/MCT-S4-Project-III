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
mqtt = MQTT(2817465839732274, q)


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

# def run_human_count():
#     global prs
#     while run and mqtt.runPrs:
#         prs = ml.count_objects()
#         time.sleep(2)
#     ml.stop()
#     print("stopped")

def run_human_count():
    while run and mqtt.runPrs:
        print("running human count")
        time.sleep(5)

def queue_listener():
    while run:
        com = q.get()
        print(com)
        if com == "people":
            print("peoplecounter started")
            actPrsCount = threading.Thread(target=run_human_count)
            actPrsCount.start()
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
        x = Sensordata("sensordata", "Kitchen", t)
        #print(x.timestamp)
        y = jsonpickle.encode(x)
        mqtt.send(y)
        print(y)
        time.sleep(5)

except Exception as ex:
    print(ex)
    run = False
    time.sleep(1)
    GPIO.cleanup()
    print("goodbye")