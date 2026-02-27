"""
Ventilator Simulator — Phase 2
Simulates current draw from ventilator machines.
"""

import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"

HOSPITALS = {
    "H001": {"ventilators": 10},
    "H002": {"ventilators": 10},
    "H003": {"ventilators": 10},
    "H004": {"ventilators": 10},
}


def main():
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)
    print("Ventilator Simulator started")

    while True:
        for fid, cfg in HOSPITALS.items():
            for v in range(cfg["ventilators"]):
                vent_id = f"VENT_{v:02d}"
                # Random current: >2A = in use, <0.5A = off
                in_use = random.random() < 0.4
                current = random.uniform(2.0, 5.0) if in_use else random.uniform(0.0, 0.3)

                payload = {
                    "facility_id": fid,
                    "resource_type": "VENTILATOR",
                    "resource_id": vent_id,
                    "raw_value": round(current, 2),
                }
                topic = f"hospital/{fid}/ventilator/raw"
                client.publish(topic, json.dumps(payload))

        time.sleep(4)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Ventilator Simulator stopped.")
