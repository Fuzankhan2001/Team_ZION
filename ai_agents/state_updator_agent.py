"""
State Updater Agent
Listens to raw MQTT sensor data and updates PostgreSQL.
"""

import json
import psycopg2
import paho.mqtt.client as mqtt
from config import BROKER, DB_PARAMS

TOPIC = "hospital/+/+/raw"



def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


def update_resource_state(conn, facility_id, resource_type, resource_id, value):
    cursor = conn.cursor()
    try:
        # UPSERT: Update the specific resource
        cursor.execute("""
            INSERT INTO hospital_resources (facility_id, resource_type, resource_id, current_value, updated_at)
            VALUES (%s, %s, %s, %s, now())
            ON CONFLICT (facility_id, resource_type, resource_id) 
            DO UPDATE SET current_value = EXCLUDED.current_value, updated_at = now();
        """, (facility_id, resource_type, resource_id, value))

        # AGGREGATE
        if resource_type == 'OXYGEN':
            cursor.execute("""
                SELECT AVG(current_value) FROM hospital_resources 
                WHERE facility_id = %s AND resource_type = 'OXYGEN'
            """, (facility_id,))
            avg_pressure = cursor.fetchone()[0] or 0
            new_percent = min(100.0, max(0.0, (avg_pressure / 2000.0) * 100.0))

            status = 'NORMAL' if new_percent > 30 else 'CRITICAL'
            cursor.execute("""
                UPDATE hospital_state 
                SET oxygen_percent = %s, oxygen_status = %s, last_updated = now()
                WHERE facility_id = %s
            """, (new_percent, status, facility_id))

        elif resource_type == 'BED':
            cursor.execute("""
                SELECT COUNT(*) FROM hospital_resources 
                WHERE facility_id = %s AND resource_type = 'BED' AND current_value > 10
            """, (facility_id,))
            occupied_count = cursor.fetchone()[0] or 0

            cursor.execute("""
                UPDATE hospital_state 
                SET beds_occupied = %s, last_updated = now()
                WHERE facility_id = %s
            """, (occupied_count, facility_id))

        conn.commit()
    except Exception as e:
        print(f"DB Logic Error: {e}")
        conn.rollback()
    finally:
        cursor.close()


def on_message(client, userdata, msg):
    conn = get_db_connection()
    if not conn:
        return

    try:
        payload = json.loads(msg.payload.decode())

        facility_id = payload.get('facility_id')
        resource_type = payload.get('resource_type')
        resource_id = payload.get('resource_id')
        raw_value = payload.get('raw_value')

        if facility_id and resource_type and resource_id is not None:
            update_resource_state(conn, facility_id, resource_type, resource_id, float(raw_value))

    except Exception as e:
        print(f"Processing Error: {e}")
    finally:
        conn.close()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("State Updater Connected. Tracking resources...")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed with code {rc}")


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping agent...")
    except Exception as e:
        print(f"MQTT Error: {e}")
