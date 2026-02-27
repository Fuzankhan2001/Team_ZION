"""
Monitoring Agent
Polls database, detects risks.
LLM explanation is a stub — will be wired in Phase 3.
"""

import psycopg2
import time
import json
from datetime import datetime
from config import DB_PARAMS, CHECK_INTERVAL_SECONDS



def get_db_connection():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def fetch_hospital_state():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.facility_id,
                s.beds_occupied,
                c.beds_total,
                s.ventilators_in_use,
                c.ventilators_total,
                s.oxygen_percent,
                s.oxygen_status
            FROM hospital_state s
            JOIN hospital_capacity c ON s.facility_id = c.facility_id
        """)

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    except Exception as e:
        print(f"Error fetching hospital state: {e}")
        return []
    finally:
        conn.close()


def detect_risks(hospital):
    risks = []
    bed_ratio = hospital["beds_occupied"] / float(hospital["beds_total"])
    vent_ratio = hospital["ventilators_in_use"] / float(hospital["ventilators_total"])

    if bed_ratio >= 0.8:
        risks.append("HIGH_BED_UTILIZATION")
    if vent_ratio >= 0.8:
        risks.append("VENTILATOR_STRESS")
    if hospital["oxygen_percent"] <= 30:
        risks.append("OXYGEN_CRITICAL")

    return risks


def generate_explanation(hospital, risks):
    """Stub — will use LLM in Phase 3"""
    return (
        f"Hospital {hospital['facility_id']} has: {', '.join(risks)}. "
        f"Resource utilization is approaching critical thresholds."
    )


def run_monitoring_agent():
    print("Monitoring Agent started")
    print(f"  Checking every {CHECK_INTERVAL_SECONDS} seconds\n")

    while True:
        try:
            hospitals = fetch_hospital_state()
            if not hospitals:
                print("No hospital data available")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            for hospital in hospitals:
                risks = detect_risks(hospital)
                if risks:
                    explanation = generate_explanation(hospital, risks)
                    alert = {
                        "alert_type": "HOSPITAL_RISK",
                        "facility_id": hospital["facility_id"],
                        "risks": risks,
                        "generated_at": datetime.utcnow().isoformat() + "Z",
                        "explanation": explanation
                    }
                    print("\n" + "=" * 60)
                    print("ALERT GENERATED")
                    print("=" * 60)
                    print(json.dumps(alert, indent=2))

        except KeyboardInterrupt:
            print("\nMonitoring agent stopped")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    test_conn = get_db_connection()
    if test_conn:
        print("Database connection successful")
        test_conn.close()
        run_monitoring_agent()
    else:
        print("Cannot start: Database connection failed")
        exit(1)
