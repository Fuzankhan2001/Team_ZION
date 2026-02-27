"""
Ventilator Preprocessor — Phase 3
Converts current draw readings to ventilator status events.
"""

import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
CURRENT_THRESHOLD = 1.5  # Above this amperage = in use

vent_last_state = {}


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        fid = data["facility_id"]
        vent_id = data["resource_id"]
        current = data["raw_value"]

        in_use = current > CURRENT_THRESHOLD
        key = (fid, vent_id)
        prev = vent_last_state.get(key, None)

        if prev != in_use:
            vent_last_state[key] = in_use
            event = {
                "facility_id": fid,
                "event_type": "VENTILATOR_STATUS",
                "status": "IN_USE" if in_use else "FREE",
                "ventilator_id": vent_id,
            }
            client.publish("events/ventilator_status", json.dumps(event))
            print(f"  Vent {vent_id} at {fid}: {'IN_USE' if in_use else 'FREE'}")

    except Exception as e:
        print(f"Preprocessor error: {e}")


def on_connect(client, userdata, flags, rc):
    print("Ventilator Preprocessor connected")
    client.subscribe("hospital/+/ventilator/raw")


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Ventilator Preprocessor stopped.")
