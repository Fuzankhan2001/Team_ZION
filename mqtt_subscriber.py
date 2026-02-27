"""
MQTT Debug Subscriber — Phase 2
Prints all MQTT messages for debugging.
"""

import json
import paho.mqtt.client as mqtt

BROKER = "localhost"


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"[{msg.topic}] {json.dumps(data, indent=2)}")
    except:
        print(f"[{msg.topic}] {msg.payload.decode()}")


def on_connect(client, userdata, flags, rc):
    print("Debug subscriber connected — listening to #")
    client.subscribe("#")


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Stopped.")
