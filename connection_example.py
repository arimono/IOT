import mysql.connector
import paho.mqtt.client as paho

# DB
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=""
)
# mqtt
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.username_pw_set("Username", "Password")
client.connect("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.s1.eu.hivemq.cloud", 8883) 