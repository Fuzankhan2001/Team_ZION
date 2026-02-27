"""
Hospital Aggregator
Listens to MQTT events and will aggregate per-hospital state.
"""

import json
from collections import defaultdict
import paho.mqtt.client as mqtt

from config import BROKER, MQTT_PORT
TOPIC = "events/#"

hospital_state = defaultdict(lambda: {
    "beds_occupied": 0,
    "ventilators_in_use": 0,
    "oxygen_percent": 100.0,
})


def handle_event(event):
    """Process incoming events"""
    pass


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        event = json.loads(payload)
        handle_event(event)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed: {rc}")


if __name__ == "__main__":
    print("Hospital Aggregator — starting...")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("Stopped.")
