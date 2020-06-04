from Logic.mqtt_pub_sub import MQTT
import time
import queue

q = queue.Queue()

mqtt =MQTT(2908911338724843, q)

while True:
    time.sleep(2)