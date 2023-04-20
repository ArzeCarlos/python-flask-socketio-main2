from flask import Flask, render_template, request
from flask_socketio import SocketIO
import random
import json
from threading import Lock
from datetime import datetime
from paho.mqtt import client as mqtt_client
"""
    MQTT BROKER PARAMETERS
"""
broker = 'ec2-3-89-120-16.compute-1.amazonaws.com'
port = 1883
topic = "testtopic/1"
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'test'
password = '12345'
"""
Connect MQTT broker
"""
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
"""
Subscribe MQTT broker
"""
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        x=msg.payload.decode()
        y=json.loads(x)
        socketio.emit('updateSensorData', {'value':y["humidity"], "date": get_current_datetime()})
        socketio.sleep(1)
    client.subscribe(topic)
    client.on_message = on_message
    print (client.on_message)
   
"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')

"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

"""
Generate random sequence of dummy sensor values and send it to our clients
"""
def background_thread():
    print("Generating random sensor values")
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

"""
Serve root index file
"""
@app.route('/')
def index():
    return render_template('index.html')

"""
Decorator for connect
"""
@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

if __name__ == '__main__':
    socketio.run(app)