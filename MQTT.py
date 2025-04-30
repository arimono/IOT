from connection import client
import json
from models import update
import threading
import time

# Global state
last_temp = None
last_humidity = None
last_update_time = 0
lock = threading.Lock()

# ========== MQTT Callbacks ==========

def on_connect(client, userdata, flags, rc, properties=None):
    print("MQTT received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    global last_temp, last_humidity, last_update_time
    # print(msg.topic)
    # print(str(msg.qos))
    try:
        iotMsg = msg.payload
        iotMsg_dict = json.loads(iotMsg.decode('utf-8'))
        # print(iotMsg_dict)
        cur_temp = None
        cur_humidity = None
        # search temp and humidity in dict
        for device in iotMsg_dict['devices']:
            if device['id'] == 'sensor_temp':
                for trait in device['traits']:
                    if trait['name'] == 'TemperatureSetting':
                        cur_temp = trait['values']['thermostatTemperatureAmbient']
                        print(f"Temperature Sensor Ambient Temperature: {cur_temp}")
            if device['id'] == 'sensor_humidity':
                for trait in device['traits']:
                    if trait['name'] == 'TemperatureSetting':
                        cur_humidity = trait['values']['thermostatTemperatureAmbient']
                        print(f"Humidity Sensor Ambient Temperature: {cur_humidity}")

        if cur_temp is not None and cur_humidity is not None:
            with lock:
                last_temp = cur_temp
                last_humidity = cur_humidity
                last_update_time = time.time()
            update("sensor", ("temp", "humidity"), (last_temp, last_humidity))
            print("[Immediate Update] Received MQTT data and saved.")
            print("-------------------------------------------------------------------------------------")

        # update the last known good value if ping is recieved.
        if iotMsg_dict['type'] == 'ping':
            if last_temp is not None and last_humidity is not None:
                with lock:
                    update("sensor", ("temp", "humidity"), (last_temp, last_humidity))
                    last_update_time = time.time()
                    print(f"Last Temperature Sensor Ambient Temperature: {last_temp}")
                    print(f"Last Humidity Sensor Ambient Temperature: {last_humidity}")
                    print("[Update] Heartbeat recieved, saved last known values.")
                    print("-------------------------------------------------------------------------------------")
    except Exception as e:
        print(f"[ERROR] Failed to process MQTT message: {e}")

def backup_update_loop():
    global last_update_time
    while True:
        time.sleep(10)
        with lock:
            if last_temp is not None and last_humidity is not None:
                now = time.time()
                if now - last_update_time >= 120:
                    update("sensor", ("temp", "humidity"), (None, None))
                    last_update_time = now
                    print("[Update] No heartbeat is recieved in 2 minutes, saved null values")
                    print("-------------------------------------------------------------------------------------")

threading.Thread(target=backup_update_loop, daemon=True).start()

# ========== MQTT Setup ==========

client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe("iot/control/#", qos=1)
client.loop_forever()