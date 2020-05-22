from Sensors.Mcp import Mcp
import RPi.GPIO as GPIO
from Sensors.dht11 import DHT11
from Sensors.klasseknop import Button
import time
import threading

GPIO.setmode(GPIO.BCM)

run = True

light = 0
temp = 0
hmdt = 0

mcp = Mcp(0,0)
dht = DHT11(pin=17)

def run_light():
    global light
    while run:
        light = mcp.read_channel(2) / 1024 * 100

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

try:
    actLight = threading.Thread(target=run_light)
    actLight.start()
    actTemp = threading.Thread(target=run_temp)
    actTemp.start()
    actHmdt = threading.Thread(target=run_hmdt)
    actHmdt.start()

    while (True):
        print("light: %f%%" % light)
        print("temperature: %f°C" % temp)
        print("humidity: %d%%" % hmdt)
        print("")
        time.sleep(0.5)

except Exception as ex:
    print(ex)
    run = False
    time.sleep(1)
    GPIO.cleanup()
    print("goodbye")