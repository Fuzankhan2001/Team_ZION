"""
Bed Simulator — Phase 2
Full pressure sensor simulation with per-bed IDs.
Publishes to hospital/{facility_id}/bed/raw
"""

import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"

HOSPITALS = {
    "H001": {"beds": 10},
    "H002": {"beds": 10},
    "H003": {"beds": 10},
    "H004": {"beds": 10},
}

# Track per-bed state
bed_states = {}
for fid, cfg in HOSPITALS.items():
    for b in range(cfg["beds"]):
        bed_states[(fid, f"BED_{b:02d}")] = random.choice([True, False])


def main():
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)
    print("Bed Simulator started — publishing to hospital/+/bed/raw")

    while True:
        for (fid, bed_id), occupied in bed_states.items():
            # Random state change with 10% probability
            if random.random() < 0.10:
                occupied = not occupied
                bed_states[(fid, bed_id)] = occupied

            # Occupied beds have high pressure, empty beds low
            pressure = random.uniform(30, 80) if occupied else random.uniform(0, 5)

            payload = {
                "facility_id": fid,
                "resource_type": "BED",
                "resource_id": bed_id,
                "raw_value": round(pressure, 2),
            }
            topic = f"hospital/{fid}/bed/raw"
            client.publish(topic, json.dumps(payload))

        time.sleep(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bed Simulator stopped.")
