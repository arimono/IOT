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

    print(msg.topic)
    print("---------------------------------------------------------------------------")
    print(str(msg.qos))
    print("---------------------------------------------------------------------------")
    
    try:
        iotMsg = msg.payload
        iotMsg_dict = json.loads(iotMsg.decode('utf-8'))
        print(iotMsg_dict)
        print("---------------------------------------------------------------------------")

        temp = None
        humidity = None

        for device in iotMsg_dict['devices']:
            if device['id'] == 'sensor_temp':
                for trait in device['traits']:
                    if trait['name'] == 'TemperatureSetting':
                        temp = trait['values']['thermostatTemperatureAmbient']
                        print(f"Temperature Sensor Ambient Temperature: {temp}")
            if device['id'] == 'sensor_humidity':
                for trait in device['traits']:
                    if trait['name'] == 'TemperatureSetting':
                        humidity = trait['values']['thermostatTemperatureAmbient']
                        print(f"Humidity Sensor Ambient Temperature: {humidity}")

        if temp is not None and humidity is not None:
            with lock:
                last_temp = temp
                last_humidity = humidity
                last_update_time = time.time()
            update("sensor", ("temp", "humidity"), (last_temp, last_humidity))
            print("[Immediate Update] Received MQTT data and saved.")
            print("---------------------------------------------------------------------------")
    except Exception as e:
        print(f"[ERROR] Failed to process MQTT message: {e}")

# ========== Background Thread ==========

def backup_update_loop():
    global last_update_time
    while True:
        time.sleep(10)
        with lock:
            if last_temp is not None and last_humidity is not None:
                now = time.time()
                if now - last_update_time >= 60:
                    update("sensor", ("temp", "humidity"), (last_temp, last_humidity))
                    last_update_time = now
                    print("[Backup Update] No new data, saved last known values.")
                    print("---------------------------------------------------------------------------")

# Start background thread
threading.Thread(target=backup_update_loop, daemon=True).start()

# ========== MQTT Setup ==========

client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

client.subscribe("iot/control/#", qos=1)
client.loop_forever()