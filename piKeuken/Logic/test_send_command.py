from google.cloud import iot_v1
import jsonpickle
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/cert.json'

registry_id="OfficeOfTheFuture"
cloud_region="europe-west1"
project_id="engaged-context-277613"
device_id=3052736401110405
command = jsonpickle.encode({"people":"off"})

print('Sending command to device')
client = iot_v1.DeviceManagerClient()
device_path = client.device_path(
    project_id, cloud_region, registry_id, device_id)

# command = 'Hello IoT Core!'
data = command.encode('utf-8')

print(client.send_command_to_device(device_path, data))