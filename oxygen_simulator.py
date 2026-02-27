"""
Oxygen Simulator — Phase 2
Simulates oxygen cylinder pressure readings.
"""

import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"

HOSPITALS = {
    "H001": {"oxygen_cylinders": 4},
    "H002": {"oxygen_cylinders": 4},
    "H003": {"oxygen_cylinders": 4},
    "H004": {"oxygen_cylinders": 4},
}

# Track cylinder pressure (starts full at ~2000 PSI)
cylinder_state = {}
for fid, cfg in HOSPITALS.items():
    for o in range(cfg["oxygen_cylinders"]):
        cylinder_state[(fid, f"OXY_{o:02d}")] = random.uniform(1500, 2000)


def main():
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)
    print("Oxygen Simulator started")

    while True:
        for (fid, oxy_id), pressure in cylinder_state.items():
            # Slowly drain pressure
            drain = random.uniform(5, 30)
            pressure = max(0, pressure - drain)

            # Occasionally refill (10% chance when low)
            if pressure < 200 and random.random() < 0.10:
                pressure = random.uniform(1800, 2000)

            cylinder_state[(fid, oxy_id)] = pressure

            payload = {
                "facility_id": fid,
                "resource_type": "OXYGEN",
                "resource_id": oxy_id,
                "raw_value": round(pressure, 2),
            }
            topic = f"hospital/{fid}/oxygen/raw"
            client.publish(topic, json.dumps(payload))

        time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Oxygen Simulator stopped.")
