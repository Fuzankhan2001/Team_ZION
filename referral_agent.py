import psycopg2
import math
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

llm_client = g4f.Client()

# ---------------- DB CONNECTION ----------------

def get_db_connection():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

# ---------------- UTILITIES ----------------

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ---------------- DB FETCH ----------------

def fetch_hospitals():
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                h.facility_id,
                h.name,
                h.latitude,
                h.longitude,
                s.beds_occupied,
                c.beds_total,
                s.ventilators_in_use,
                c.ventilators_total,
                s.oxygen_percent,
                s.oxygen_status
            FROM hospitals h
            JOIN hospital_state s ON h.facility_id = s.facility_id
            JOIN hospital_capacity c ON h.facility_id = c.facility_id
            WHERE c.beds_total > 0 AND c.ventilators_total > 0
        """)

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    except Exception as e:
        print(f"❌ Error fetching hospitals: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        conn.close()

# ---------------- SCORING ----------------

def score_hospital(h, ambulance_loc):
    """Score a hospital based on multiple factors"""
    score = 100

    try:
        beds_available = h["beds_total"] - h["beds_occupied"]
        vents_available = h["ventilators_total"] - h["ventilators_in_use"]

        distance_km = haversine(
            ambulance_loc["lat"],
            ambulance_loc["lon"],
            h["latitude"],
            h["longitude"]
        )

        # Distance penalty (closer is better)
        score -= distance_km * 1.5

        # Capacity penalties
        if beds_available <= 0:
            score -= 40
        if vents_available <= 0:
            score -= 50

        # Stress penalties (avoid overloaded hospitals)
        bed_ratio = h["beds_occupied"] / float(h["beds_total"])
        vent_ratio = h["ventilators_in_use"] / float(h["ventilators_total"])
        
        if bed_ratio >= 0.8:
            score -= 15
        if vent_ratio >= 0.8:
            score -= 20

        # Oxygen penalty
        if h["oxygen_percent"] <= 30:
            score -= 30

        return round(score, 2), round(distance_km, 2)
    
    except Exception as e:
        print(f"❌ Scoring error for {h.get('facility_id', 'UNKNOWN')}: {e}")
        return 0.0, 999.0

# ---------------- AI EXPLANATION ----------------

def generate_explanation(request, ranked_hospitals):
    """Generate AI explanation for referral recommendation"""
    try:
        prompt = f"""
You are a hospital referral assistant.

Patient condition:
- Severity: {request['patient_severity']}
- Required resource: {request['required_resource']}

Top 3 hospitals:
{json.dumps(ranked_hospitals, indent=2)}

Explain in 3-4 sentences:
- Why the top hospital is recommended
- Key factors in the decision
- Any concerns about alternatives
- Keep explanation operational, not medical
"""

        response = llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            timeout=15
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"⚠️  LLM explanation failed, using fallback: {e}")
        
        # Fallback explanation
        top = ranked_hospitals[0]
        return (
            f"{top['hospital_name']} is recommended based on: "
            f"{top['distance_km']}km distance, "
            f"{top['beds_available']} beds available, "
            f"{top['ventilators_available']} ventilators available, "
            f"and {top['oxygen_percent']}% oxygen level. "
            f"This facility has the best balance of proximity and resource availability."
        )

# ---------------- MAIN FUNCTION ----------------

def handle_referral(request):
    """Process a referral request and return recommendations"""
    print("\n" + "="*60)
    print("🚑 PROCESSING REFERRAL REQUEST")
    print("="*60)
    print(f"Severity: {request['patient_severity']}")
    print(f"Required: {request['required_resource']}")
    print(f"Location: {request['ambulance_location']}")
    print("="*60 + "\n")
    
    hospitals = fetch_hospitals()
    
    if not hospitals:
        return {
            "error": "No hospitals available",
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    
    ranked = []

    for h in hospitals:
        score, distance = score_hospital(h, request["ambulance_location"])
        ranked.append({
            "facility_id": h["facility_id"],
            "hospital_name": h["name"],
            "score": score,
            "distance_km": distance,
            "beds_available": h["beds_total"] - h["beds_occupied"],
            "ventilators_available": h["ventilators_total"] - h["ventilators_in_use"],
            "oxygen_percent": h["oxygen_percent"]
        })

    # Sort by score (highest first)
    ranked.sort(key=lambda x: x["score"], reverse=True)

    # Generate explanation for top 3
    top_3 = ranked[:3]
    explanation = generate_explanation(request, top_3)

    result = {
        "request_id": f"REF_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "recommendations": top_3,
        "all_hospitals_count": len(ranked),
        "explanation": explanation
    }
    
    print("✓ Referral generated successfully\n")
    return result

# ---------------- DEMO RUN ----------------

if __name__ == "__main__":
    # Test database connection
    test_conn = get_db_connection()
    if not test_conn:
        print("❌ Cannot start: Database connection failed")
        exit(1)
    
    print("✓ Database connection successful")
    test_conn.close()
    
    # Demo referral request
    referral_request = {
        "patient_severity": "CRITICAL",
        "required_resource": "VENTILATOR",
        "ambulance_location": {
            "lat": 18.5204,
            "lon": 73.8567
        }
    }

    response = handle_referral(referral_request)
    
    print("\n" + "="*60)
    print("📋 REFERRAL RESPONSE")
    print("="*60)
    print(json.dumps(response, indent=2))
    print("="*60)