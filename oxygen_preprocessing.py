"""
Oxygen Preprocessor — Phase 3
Converts cylinder pressure to oxygen level percentage + status.
"""

import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
MAX_PRESSURE = 2000.0  # Full cylinder PSI

oxy_last_state = {}


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        fid = data["facility_id"]
        oxy_id = data["resource_id"]
        pressure = data["raw_value"]

        level_percent = min(100.0, max(0.0, (pressure / MAX_PRESSURE) * 100.0))

        if level_percent <= 20:
            status = "CRITICAL"
        elif level_percent <= 40:
            status = "WARNING"
        else:
            status = "NORMAL"

        key = (fid, oxy_id)
        prev_status = oxy_last_state.get(key, None)

        # Always emit level, but only log on status change
        event = {
            "facility_id": fid,
            "event_type": "OXYGEN_LEVEL",
            "estimated_level_percent": round(level_percent, 1),
            "status": status,
            "cylinder_id": oxy_id,
        }
        client.publish("events/oxygen_level", json.dumps(event))

        if prev_status != status:
            oxy_last_state[key] = status
            print(f"  O₂ {oxy_id} at {fid}: {level_percent:.1f}% ({status})")

    except Exception as e:
        print(f"Preprocessor error: {e}")


def on_connect(client, userdata, flags, rc):
    print("Oxygen Preprocessor connected")
    client.subscribe("hospital/+/oxygen/raw")


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Oxygen Preprocessor stopped.")
