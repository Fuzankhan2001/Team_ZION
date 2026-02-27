"""
Bed Preprocessor — Phase 2
Converts raw pressure readings to occupancy events.
Publishes to events/bed_occupancy
"""

import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PRESSURE_THRESHOLD = 10  # Above this = occupied

bed_last_state = {}


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        fid = data["facility_id"]
        bed_id = data["resource_id"]
        pressure = data["raw_value"]

        current_occupied = pressure > PRESSURE_THRESHOLD
        key = (fid, bed_id)
        prev_occupied = bed_last_state.get(key, None)

        # Only emit on state change
        if prev_occupied != current_occupied:
            bed_last_state[key] = current_occupied
            event = {
                "facility_id": fid,
                "event_type": "BED_OCCUPANCY",
                "occupancy_state": "OCCUPIED" if current_occupied else "FREE",
                "bed_id": bed_id,
            }
            client.publish("events/bed_occupancy", json.dumps(event))
            print(f"  Bed {bed_id} at {fid}: {'OCCUPIED' if current_occupied else 'FREE'}")

    except Exception as e:
        print(f"Preprocessor error: {e}")


def on_connect(client, userdata, flags, rc):
    print("Bed Preprocessor connected")
    client.subscribe("hospital/+/bed/raw")


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Bed Preprocessor stopped.")
