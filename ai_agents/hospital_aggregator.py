"""
Hospital Aggregator
Full event handling: BED_OCCUPANCY, VENTILATOR_STATUS, OXYGEN_LEVEL.
Emits deltas to MQTT for the state updater.
"""

import json
from datetime import datetime, UTC
from collections import defaultdict
import paho.mqtt.client as mqtt

from config import BROKER, MQTT_PORT
TOPIC = "events/#"

hospital_state = defaultdict(lambda: {
    "beds_occupied": 0,
    "ventilators_in_use": 0,
    "oxygen_percent": 100.0,
    "oxygen_status": "NORMAL"
})

message_count = defaultdict(int)


def emit_hospital_delta(facility_id, delta):
    """Emit state changes to the database updater"""
    if not delta:
        return

    output = {
        "facility_id": facility_id,
        "delta": delta,
        "timestamp": datetime.now(UTC).isoformat() + "Z"
    }
    print(f"\n{'='*60}")
    print(f"HOSPITAL DELTA: {facility_id}")
    print(f"{'='*60}")
    print(json.dumps(output, indent=2))

    try:
        client.publish("hospital_delta/updates", json.dumps(output))
    except Exception as e:
        print(f"Failed to publish delta: {e}")


def handle_event(event):
    """Process incoming events and generate deltas"""
    if not isinstance(event, dict):
        return

    if "facility_id" not in event or "event_type" not in event:
        return

    facility = event["facility_id"]
    state = hospital_state[facility]
    delta = {}

    message_count[facility] += 1

    # -------- BED OCCUPANCY --------
    if event["event_type"] == "BED_OCCUPANCY":
        occupancy_state = event.get("occupancy_state")

        if occupancy_state == "OCCUPIED":
            state["beds_occupied"] += 1
            delta["beds_occupied"] = +1

        elif occupancy_state == "FREE":
            if state["beds_occupied"] > 0:
                state["beds_occupied"] -= 1
                delta["beds_occupied"] = -1

    # -------- VENTILATOR STATUS --------
    elif event["event_type"] == "VENTILATOR_STATUS":
        status = event.get("status")

        if status == "IN_USE":
            state["ventilators_in_use"] += 1
            delta["ventilators_in_use"] = +1

        elif status == "FREE":
            if state["ventilators_in_use"] > 0:
                state["ventilators_in_use"] -= 1
                delta["ventilators_in_use"] = -1

    # -------- OXYGEN LEVEL --------
    elif event["event_type"] == "OXYGEN_LEVEL":
        new_percent = event.get("estimated_level_percent")
        new_status = event.get("status")

        if new_percent is not None and state["oxygen_percent"] != new_percent:
            state["oxygen_percent"] = new_percent
            delta["oxygen_percent"] = new_percent

        if new_status and state["oxygen_status"] != new_status:
            state["oxygen_status"] = new_status
            delta["oxygen_status"] = new_status

    # Emit delta if there were changes
    if delta:
        emit_hospital_delta(facility, delta)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        event = json.loads(payload)
        handle_event(event)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON received: {e}")
    except Exception as e:
        print(f"Aggregator error: {e}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Hospital Aggregator Connected to MQTT")
        print(f"  Listening on: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed with code {rc}")


if __name__ == "__main__":
    print("=" * 60)
    print("HOSPITAL AGGREGATOR")
    print("=" * 60)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nAggregator stopped")
    except Exception as e:
        print(f"Error: {e}")
