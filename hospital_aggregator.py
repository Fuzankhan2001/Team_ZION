import json
from datetime import datetime
from collections import defaultdict
import paho.mqtt.client as mqtt

BROKER = "localhost"
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
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    print(f"\n{'='*60}")
    print(f"📊 HOSPITAL DELTA: {facility_id}")
    print(f"{'='*60}")
    print(json.dumps(output, indent=2))
    print(f"{'='*60}\n")
    
    try:
        client.publish("hospital_delta/updates", json.dumps(output))
    except Exception as e:
        print(f"❌ Failed to publish delta: {e}")

def handle_event(event):
    """Process incoming events and generate deltas"""
    
    # Validate event structure
    if not isinstance(event, dict):
        print("⚠️  Invalid event: not a dictionary")
        return
    
    if "facility_id" not in event or "event_type" not in event:
        print("⚠️  Invalid event: missing required fields")
        return
    
    facility = event["facility_id"]
    state = hospital_state[facility]
    delta = {}
    
    message_count[facility] += 1

    try:
        # -------- BED OCCUPANCY --------
        if event["event_type"] == "BED_OCCUPANCY":
            occupancy_state = event.get("occupancy_state")
            
            if occupancy_state == "OCCUPIED":
                state["beds_occupied"] += 1
                delta["beds_occupied"] = +1
                print(f"  🛏️  Bed occupied at {facility} (Total: {state['beds_occupied']})")
                
            elif occupancy_state == "FREE":
                if state["beds_occupied"] > 0:
                    state["beds_occupied"] -= 1
                    delta["beds_occupied"] = -1
                    print(f"  🛏️  Bed freed at {facility} (Total: {state['beds_occupied']})")
                else:
                    print(f"  ⚠️  Bed free event ignored - already at 0")

        # -------- VENTILATOR STATUS --------
        elif event["event_type"] == "VENTILATOR_STATUS":
            status = event.get("status")
            
            if status == "IN_USE":
                state["ventilators_in_use"] += 1
                delta["ventilators_in_use"] = +1
                print(f"  🫁 Ventilator in use at {facility} (Total: {state['ventilators_in_use']})")
                
            elif status == "FREE":
                if state["ventilators_in_use"] > 0:
                    state["ventilators_in_use"] -= 1
                    delta["ventilators_in_use"] = -1
                    print(f"  🫁 Ventilator freed at {facility} (Total: {state['ventilators_in_use']})")
                else:
                    print(f"  ⚠️  Ventilator free event ignored - already at 0")

        # -------- OXYGEN LEVEL --------
        elif event["event_type"] == "OXYGEN_LEVEL":
            new_percent = event.get("estimated_level_percent")
            new_status = event.get("status")
            
            # Only emit if values actually changed
            if new_percent is not None and state["oxygen_percent"] != new_percent:
                old_percent = state["oxygen_percent"]
                state["oxygen_percent"] = new_percent
                delta["oxygen_percent"] = new_percent
                print(f"  💨 Oxygen level changed at {facility}: {old_percent:.1f}% → {new_percent:.1f}%")
            
            if new_status and state["oxygen_status"] != new_status:
                old_status = state["oxygen_status"]
                state["oxygen_status"] = new_status
                delta["oxygen_status"] = new_status
                print(f"  💨 Oxygen status changed at {facility}: {old_status} → {new_status}")
        
        else:
            print(f"  ⚠️  Unknown event type: {event['event_type']}")

        # Emit delta if there were changes
        if delta:
            emit_hospital_delta(facility, delta)
            
    except Exception as e:
        print(f"❌ Error handling event for {facility}: {e}")
        import traceback
        traceback.print_exc()

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        event = json.loads(payload)
        handle_event(event)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON received: {e}")
    except Exception as e:
        print(f"❌ Aggregator error: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("="*60)
        print("✓ Hospital Aggregator Connected to MQTT")
        print(f"  Listening on: {TOPIC}")
        print("="*60 + "\n")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"⚠️  Unexpected disconnection. Reconnecting...")

# -------- PERIODIC STATS --------
def print_stats():
    """Print aggregator statistics every 30 seconds"""
    print("\n" + "="*60)
    print("📈 AGGREGATOR STATISTICS")
    print("="*60)
    for facility, count in sorted(message_count.items()):
        state = hospital_state[facility]
        print(f"{facility}: {count} events processed")
        print(f"  Beds: {state['beds_occupied']}, Vents: {state['ventilators_in_use']}, "
              f"O2: {state['oxygen_percent']:.1f}% ({state['oxygen_status']})")
    print("="*60 + "\n")

# -------- MAIN --------
if __name__ == "__main__":
    print("="*60)
    print("🏥 HOSPITAL AGGREGATOR")
    print("="*60 + "\n")
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Enable automatic reconnection
    client.reconnect_delay_set(min_delay=1, max_delay=120)
    
    try:
        client.connect(BROKER, 1883, 60)
        
        # Optional: Print stats periodically
        # import threading
        # def stats_loop():
        #     while True:
        #         time.sleep(30)
        #         print_stats()
        # threading.Thread(target=stats_loop, daemon=True).start()
        
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n✓ Aggregator stopped")
    except Exception as e:
        print(f"❌ Error: {e}")