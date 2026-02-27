"""
Monitoring Agent
Polls database, detects risks, and generates LLM explanations.
"""

import os
import psycopg
import time
import json
import traceback
from datetime import datetime, UTC
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from config import (
    DB_PARAMS, 
    CHECK_INTERVAL_SECONDS, 
    LLM_MODEL, 
    LLM_API_VERSION,
    LLM_TIMEOUT,
    BED_THRESHOLD,
    VENT_THRESHOLD,
    OXYGEN_CRITICAL
)

# Load .env from project root (one level up from ai_agents/)
load_dotenv(Path(__file__).parent.parent / ".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY, http_options={"api_version": LLM_API_VERSION})

# Cache: only call LLM when a hospital's risks actually change
last_known_risks: dict = {}


def get_db_connection():
    try:
        return psycopg.connect(**DB_PARAMS)
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
            WHERE c.beds_total > 0 AND c.ventilators_total > 0
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
    try:
        if hospital["beds_total"] == 0 or hospital["ventilators_total"] == 0:
            return risks

        bed_ratio = hospital["beds_occupied"] / float(hospital["beds_total"])
        vent_ratio = hospital["ventilators_in_use"] / float(hospital["ventilators_total"])

        if bed_ratio >= BED_THRESHOLD:
            risks.append("HIGH_BED_UTILIZATION")
        if vent_ratio >= VENT_THRESHOLD:
            risks.append("VENTILATOR_STRESS")
        if hospital["oxygen_percent"] <= OXYGEN_CRITICAL:
            risks.append("OXYGEN_CRITICAL")

    except Exception as e:
        print(f"Risk detection error for {hospital.get('facility_id', 'UNKNOWN')}: {e}")

    return risks


def generate_explanation(hospital, risks):
    """Generate LLM-powered explanation with fallback."""
    try:
        prompt = f"""
You are a hospital operations monitoring assistant.

Hospital ID: {hospital['facility_id']}

Current State:
- Beds occupied: {hospital['beds_occupied']} / {hospital['beds_total']}
- Ventilators in use: {hospital['ventilators_in_use']} / {hospital['ventilators_total']}
- Oxygen level: {hospital['oxygen_percent']}%
- Oxygen status: {hospital['oxygen_status']}

Detected Risks: {', '.join(risks)}

Explain:
- Why this situation is risky
- What hospital administrators should be aware of
- Keep explanation factual and non-medical
- Be concise (2-3 sentences)
"""

        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
        )
        return response.text

    except Exception as e:
        print(f"LLM call failed, using fallback: {e}")
        return (
            f"Hospital {hospital['facility_id']} is experiencing: "
            f"{', '.join(risks)}. "
            f"Resource utilization is approaching critical thresholds. "
            f"Administrators should monitor availability and prepare mitigation actions."
        )


def run_monitoring_agent():
    print("Monitoring Agent started (READ-ONLY)")
    print(f"  Checking every {CHECK_INTERVAL_SECONDS} seconds\n")

    while True:
        try:
            hospitals = fetch_hospital_state()
            if not hospitals:
                print("No hospital data available or database connection failed")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            for hospital in hospitals:
                fid = hospital["facility_id"]
                risks = detect_risks(hospital)
                if risks:
                    risks_key = tuple(sorted(risks))
                    risks_changed = last_known_risks.get(fid) != risks_key

                    if risks_changed:
                        explanation = generate_explanation(hospital, risks)
                        last_known_risks[fid] = risks_key
                    else:
                        # Risks unchanged — reuse last explanation, skip LLM call
                        explanation = (
                            f"Hospital {fid} continues to experience: {', '.join(risks)}. "
                            f"No change since last alert."
                        )

                    alert = {
                        "alert_type": "HOSPITAL_RISK",
                        "facility_id": fid,
                        "risks": risks,
                        "generated_at": datetime.now(UTC).isoformat() + "Z",
                        "explanation": explanation
                    }
                    print("\n" + "=" * 60)
                    print("ALERT GENERATED" + (" [NEW]" if risks_changed else " [ONGOING]"))
                    print("=" * 60)
                    print(json.dumps(alert, indent=2))
                    print("=" * 60 + "\n")
                else:
                    # Risks cleared — reset cache so next occurrence triggers LLM again
                    last_known_risks.pop(fid, None)

        except KeyboardInterrupt:
            print("\nMonitoring agent stopped by user")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            traceback.print_exc()

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
