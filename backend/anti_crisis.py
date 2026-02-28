import psycopg2
from psycopg2.extras import RealDictCursor
import time
import random

# DB CONFIG
DB_CONFIG = {
    "dbname": "hospitaldb",
    "user": "postgres",
    "password": "posthack", 
    "host": "localhost",
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def trigger_crisis(hospital_id="H001"):
    conn = get_db_connection()
    cur = conn.cursor()
    
    print(f"🚨 INITIATING CRISIS PROTOCOL FOR {hospital_id}...")
    
    # 1. Update LIVE DASHBOARD to Critical
    # Oxygen drops to 82% (Warning/Critical), Beds fill up
    cur.execute("""
        UPDATE hospital_state 
        SET oxygen_percent = 82.0, 
            beds_occupied = 5, 
            ventilators_in_use = 5,
            oxygen_status = 'CRITICAL'
        WHERE facility_id = %s
    """, (hospital_id,))
    
    # 2. Inject BAD HISTORY (so the AI sees a downward trend)
    # We insert records showing oxygen dropping rapidly over the last 30 mins
    cur.execute("""
        INSERT INTO hospital_history (facility_id, beds_occupied, oxygen_percent, recorded_at) VALUES 
        (%s, 40, 95.0, NOW() - INTERVAL '30 minutes'),
        (%s, 42, 92.0, NOW() - INTERVAL '20 minutes'),
        (%s, 45, 88.0, NOW() - INTERVAL '10 minutes'),
        (%s, 48, 82.0, NOW());
    """, (hospital_id, hospital_id, hospital_id, hospital_id))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"⚠️  CRITICAL STATUS SET. {hospital_id} is now Red.")

if __name__ == "__main__":
    trigger_crisis("H001") # Forces Bharati Hospital to crash