from Logic.hx711 import HX711
import time
from RPi import GPIO
from Logic.mqtt_pub_sub import MQTT
from Models.data import Data
from Models.sensordata import Sensordata
import jsonpickle
import queue
import threading
GPIO.setmode(GPIO.BCM)

hx = HX711(20, 21)
hx.set_offset(1255.226245605469)
q = queue.Queue()
mqtt = MQTT(2938279615337930, q)
run = True
#hx.set_offset(8330161.230859375)
#hx.set_scale(-100)

def queue_listener():
    global actPrs
    global run
    while run:
        com = q.get()
        if com == "quit":
            run = False
            time.sleep(5)
            break
        else:
            print("command not found")
    print("queuelistener stopped")




try:
    actQueueListener = threading.Thread(target=queue_listener)
    actQueueListener.start()
    while run:
        if mqtt.runCoffee:
            w = max(0, int(hx.get_weight(5) / 200))
            t = []
            t.append(Data("weight", w))
            x = Sensordata("sensordata", "Coffee", t)
            y = jsonpickle.encode(x)
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

#het werkt