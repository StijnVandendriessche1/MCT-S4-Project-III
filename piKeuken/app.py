from Sensors.Mcp import Mcp
import RPi.GPIO as GPIO
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

GPIO.setmode(GPIO.BCM)

run = True

light = 0
temp = 0
hmdt = 0
prs = {'person': 0}

mcp = Mcp(0,0)
dht = DHT11(pin=17)
ml = MLObjectDetection()

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
    while run:
        prs = ml.count_objects()
        time.sleep(2)


try:
    actLight = threading.Thread(target=run_light)
    actLight.start()
    actTemp = threading.Thread(target=run_temp)
    actTemp.start()
    actHmdt = threading.Thread(target=run_hmdt)
    actHmdt.start()
    actPrs = threading.Thread(target=run_human_count)
    actPrs.start()
    mqtt = MQTT(2817465839732274)


    while True:
        print("light: %f%%" % light)
        print("temperature: %f°C" % temp)
        print("humidity: %d%%" % hmdt)
        print(str(prs.get('person')))
        #print("")
        t = []
        t.append(Data("temperature", temp))
        t.append(Data("light", light))
        t.append(Data("humidity", hmdt))
        t.append(Data("persons", prs.get('person')))
        x = Sensordata("sensordata", "RaspberryPiKitchen", t)
        print(x.timestamp)
        y = jsonpickle.encode(x)
        mqtt.send(y)
        #payload = '{{ "ts": {}, "temperature": {}, "light": {}, "humidity": {} }}'.format(int(time.time() * 1000000000), temp, light, hmdt)
        time.sleep(5)

except Exception as ex:
    print(ex)
    run = False
    time.sleep(1)
    GPIO.cleanup()
    print("goodbye")