from Logic.hx711 import HX711
import time
from RPi import GPIO
from Logic.mqtt_pub_sub import MQTT
from Models.data import Data
from Models.sensordata import Sensordata
import jsonpickle
GPIO.setmode(GPIO.BCM)

hx = HX711(20, 21)
hx.set_offset(1255.226245605469)
mqtt = MQTT(2938279615337930)
#hx.set_offset(8330161.230859375)
#hx.set_scale(-100)


try:
    while True:
        w = max(0, int(hx.get_weight(5)/200))
        t = []
        t.append(Data("weight", w))
        x = Sensordata("sensordata", "Coffee", t)
        y = jsonpickle.encode(x)
        mqtt.send(y)
        print(y)
        time.sleep(5)
except KeyboardInterrupt as ex:
    print("Shutting down...")
except Exception as ex:
    print("something went wrong")
    print(ex)
finally:
    try:
        run = False
        GPIO.cleanup()
        print("goodbye")
    except Exception as e:
        print(e)