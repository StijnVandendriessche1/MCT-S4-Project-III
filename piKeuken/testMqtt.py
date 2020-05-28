from Logic.mqtt_pub_sub import MQTT

test = MQTT("RaspberryPiKitchen")

for i in range(1,11):
    pl = "{'temperature':23,'humidity':53,'light':76,'device':RaspberryPiKeuken}"
    test.send(pl)