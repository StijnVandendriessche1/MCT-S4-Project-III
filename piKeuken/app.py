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

ssl_private_key_filepath = '/home/pi/rsa_private.pem'
ssl_algorithm = 'RS256' # Either RS256 or ES256
root_cert_filepath = '/home/pi/project3/keys/roots.pem'
project_id = 'engaged-context-277613'
gcp_location = 'europe-west1'
registry_id = 'OfficeOfTheFuture'
device_id = 2817465839732274

GPIO.setmode(GPIO.BCM)

run = True

light = 0
temp = 0
hmdt = 0

mcp = Mcp(0,0)
dht = DHT11(pin=17)

cur_time = datetime.datetime.utcnow()

def create_jwt():
  token = {
      'iat': cur_time,
      'exp': cur_time + datetime.timedelta(minutes=60),
      'aud': project_id
  }

  with open(ssl_private_key_filepath, 'r') as f:
    private_key = f.read()

  return jwt.encode(token, private_key, ssl_algorithm)

_CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
_MQTT_TOPIC = '/devices/{}/events'.format(device_id)

client = mqtt.Client(client_id=_CLIENT_ID)
# authorization is handled purely with JWT, no user/pass, so username can be whatever
client.username_pw_set(
    username='unused',
    password=create_jwt())

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')

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

try:
    actLight = threading.Thread(target=run_light)
    actLight.start()
    actTemp = threading.Thread(target=run_temp)
    actTemp.start()
    actHmdt = threading.Thread(target=run_hmdt)
    actHmdt.start()

    client.on_connect = on_connect
    client.on_publish = on_publish

    client.tls_set(
        ca_certs=root_cert_filepath)  # Replace this with 3rd party cert if that was used when creating registry
    client.connect('mqtt.googleapis.com', 8883)
    client.loop_start()

    while True:
        print("light: %f%%" % light)
        print("temperature: %f°C" % temp)
        print("humidity: %d%%" % hmdt)
        #print("")
        t = []
        t.append(Data("temperature", temp))
        t.append(Data("light", light))
        t.append(Data("humidity", hmdt))
        x = Sensordata("sensordata", "RaspberryPiKitchen", t)
        print(x.timestamp)
        y = jsonpickle.encode(x)
        #payload = '{{ "ts": {}, "temperature": {}, "light": {}, "humidity": {} }}'.format(int(time.time() * 1000000000), temp, light, hmdt)
        client.publish(_MQTT_TOPIC, y, qos=1)
        time.sleep(5)

except Exception as ex:
    print(ex)
    client.loop_stop()
    run = False
    time.sleep(1)
    GPIO.cleanup()
    print("goodbye")