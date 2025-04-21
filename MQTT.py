from connection import client
import json
from models import update

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("MQTT received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    
# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    print(msg.topic)
    print("---------------------------------------------------------------------------")
    print(str(msg.qos))
    print("---------------------------------------------------------------------------")
    iotMsg = msg.payload
    iotMsg_dict = json.loads(iotMsg.decode('utf-8'))
    print(iotMsg_dict)
    print("---------------------------------------------------------------------------")
    # Accessing thermostatTemperatureAmbient for the Temperature Sensor
    for device in iotMsg_dict['devices']:
        if device['id'] == 'sensor_temp':
            for trait in device['traits']:
                if trait['name'] == 'TemperatureSetting':
                    temperature_ambient_temp = trait['values']['thermostatTemperatureAmbient']
                    print(f"Temperature Sensor Ambient Temperature: {temperature_ambient_temp}")
    # Accessing thermostatTemperatureAmbient for the Humidity Sensor
    for device in iotMsg_dict['devices']:
        if device['id'] == 'sensor_humidity':
            for trait in device['traits']:
                if trait['name'] == 'TemperatureSetting':
                    temperature_ambient_humidity = trait['values']['thermostatTemperatureAmbient']
                    print(f"Humidity Sensor Ambient Temperature: {temperature_ambient_humidity}")
                    
    update("sensor",("temp","humidity"),(temperature_ambient_temp,temperature_ambient_humidity))
    print("---------------------------------------------------------------------------")
client.on_connect = on_connect
# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("iot/control/#", qos=1)

# a single publish, this can also be done in loops, etc.
# client.publish("iot/control", payload='{"devices": [{"name": "Red LED", "id": "red_led", "type": "action.devices.types.LIGHT", "nicknames": ["Red LED"], "traits": [{"name": "OnOff", "values": {"on": true}}, {"name": "Brightness", "values": {"brightness": 0}}], "deviceInfo": {"hwVersion": "1.0", "swVersion": "2.2.3", "manufacturer": "A&H Controls", "model": "LED-BULB"}, "default_names": ["LED", "Red LED"]}, {"name": "Blue LED", "id": "blue_led", "type": "action.devices.types.LIGHT", "nicknames": ["Blue LED"], "traits": [{"name": "OnOff", "values": {"on": true}}, {"name": "Brightness", "values": {"brightness": 0}}], "deviceInfo": {"hwVersion": "1.0", "swVersion": "2.2.3", "manufacturer": "A&H Controls", "model": "LED-BULB"}, "default_names": ["LED", "Blue LED"]}, {"name": "Temperature Sensor", "id": "sensor_temp", "type": "action.devices.types.THERMOSTAT", "nicknames": ["Temperature"], "traits": [{"name": "TemperatureSetting", "values": {"thermostatHumidityAmbient": 90, "activeThermostatMode": "heat", "thermostatTemperatureAmbient": 24.0, "thermostatTemperatureSetpointLow": 0, "thermostatTemperatureSetpointHigh": 100, "thermostatMode": "heat", "thermostatTemperatureSetpoint": 24.0}}], "deviceInfo": {"hwVersion": "1.0", "swVersion": "2.2.3", "manufacturer": "A&H Controls", "model": "LED-BULB"}, "default_names": ["SENSOR", "Temperature"]}, {"name": "Humidity Sensor", "id": "sensor_humidity", "type": "action.devices.types.THERMOSTAT", "nicknames": ["Humidity"], "traits": [{"name": "TemperatureSetting", "values": {"thermostatHumidityAmbient": 90, "activeThermostatMode": "cool", "thermostatTemperatureAmbient": 69.0, "thermostatTemperatureSetpointLow": 0, "thermostatTemperatureSetpointHigh": 100, "thermostatMode": "cool", "thermostatTemperatureSetpoint": 69.0}}], "deviceInfo": {"hwVersion": "1.0", "swVersion": "1.0", "manufacturer": "A&H Controls", "model": "LED-BULB"}, "default_names": ["SENSOR", "Humidity"]}], "id": "a1", "type": "register_settings"}', qos=1)

# loop_forever for simplicity, here you need to stop the loop manually
# you can also use loop_start and loop_stop
client.loop_forever()