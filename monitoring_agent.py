import psycopg2
import time
import json
from datetime import datetime
import g4f

# ---------------- CONFIG ----------------

DB_PARAMS = {
    "dbname": "hospitaldb",
    "user": "postgres",
    "password": "posthack",
    "host": "localhost",
    "port": 5432
}

CHECK_INTERVAL_SECONDS = 15

# ---------------- LLM CLIENT ----------------

llm_client = g4f.Client()

# ---------------- DB CONNECTION ----------------

def get_db_connection():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

# ---------------- DB FETCH ----------------

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
        print(f"❌ Error fetching hospital state: {e}")
        return []
    finally:
        conn.close()

# ---------------- RISK DETECTION ----------------

def detect_risks(hospital):
    risks = []

    try:
        # Prevent division by zero
        if hospital["beds_total"] == 0 or hospital["ventilators_total"] == 0:
            return risks

        bed_ratio = hospital["beds_occupied"] / float(hospital["beds_total"])
        vent_ratio = hospital["ventilators_in_use"] / float(hospital["ventilators_total"])

        if bed_ratio >= 0.8:
            risks.append("HIGH_BED_UTILIZATION")

        if vent_ratio >= 0.8:
            risks.append("VENTILATOR_STRESS")

        if hospital["oxygen_percent"] <= 30:
            risks.append("OXYGEN_CRITICAL")

    except Exception as e:
        print(f"❌ Risk detection error for {hospital.get('facility_id', 'UNKNOWN')}: {e}")

    return risks

# ---------------- LLM EXPLANATION ----------------

def generate_explanation(hospital, risks):
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

        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            timeout=10
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"⚠️  LLM call failed, using fallback: {e}")
        # Safe fallback (NO LLM)
        return (
            f"Hospital {hospital['facility_id']} is experiencing: "
            f"{', '.join(risks)}. "
            f"Resource utilization is approaching critical thresholds. "
            f"Administrators should monitor availability and prepare mitigation actions."
        )

# ---------------- MAIN LOOP ----------------

def run_monitoring_agent():
    print("✓ Monitoring Agent started (READ-ONLY)")
    print(f"  Checking every {CHECK_INTERVAL_SECONDS} seconds\n")

    while True:
        try:
            hospitals = fetch_hospital_state()

            if not hospitals:
                print("⚠️  No hospital data available")
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

                    print("\n" + "="*60)
                    print("🚨 ALERT GENERATED")
                    print("="*60)
                    print(json.dumps(alert, indent=2))
                    print("="*60 + "\n")

        except KeyboardInterrupt:
            print("\n✓ Monitoring agent stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(CHECK_INTERVAL_SECONDS)

# ---------------- START ----------------

if __name__ == "__main__":
    # Test database connection
    test_conn = get_db_connection()
    if test_conn:
        print("✓ Database connection successful")
        test_conn.close()
        run_monitoring_agent()
    else:
        print("❌ Cannot start: Database connection failed")
        exit(1)