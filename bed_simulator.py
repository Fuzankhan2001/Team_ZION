"""
Bed Simulator — Phase 1 Skeleton
Publishes simulated pressure sensor data to MQTT.
"""

import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"
FACILITIES = ["H001", "H002"]


def main():
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)
    print("Bed Simulator — connected to MQTT")

    while True:
        for fid in FACILITIES:
            # TODO: implement realistic pressure simulation
            payload = {
                "facility_id": fid,
                "sensor_type": "BED",
                "pressure": random.uniform(0, 100),
            }
            topic = f"hospital/{fid}/bed/raw"
            client.publish(topic, json.dumps(payload))
        time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped.")
