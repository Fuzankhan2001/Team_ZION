"""
Referral Agent
Full hospital scoring with haversine distance + AI explanation.
"""

import psycopg
import math
import json
import traceback
from datetime import datetime
from google import genai
from config import (
    DB_PARAMS, 
    LLM_MODEL, 
    LLM_TIMEOUT,
    BED_THRESHOLD,
    VENT_THRESHOLD,
    OXYGEN_CRITICAL,
    DISTANCE_WEIGHT,
    NO_BEDS_PENALTY,
    NO_VENTS_PENALTY,
    HIGH_BED_PENALTY,
    HIGH_VENT_PENALTY,
    LOW_OXYGEN_PENALTY
)

client = genai.Client()


def get_db_connection():
    try:
        return psycopg.connect(**DB_PARAMS)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def fetch_hospitals():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                h.facility_id, h.name, h.latitude, h.longitude,
                s.beds_occupied, c.beds_total,
                s.ventilators_in_use, c.ventilators_total,
                s.oxygen_percent, s.oxygen_status
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
        print(f"Error fetching hospitals: {e}")
        return []
    finally:
        conn.close()


def score_hospital(h, ambulance_loc):
    """Score a hospital based on distance, availability, and utilization."""
    score = 100
    try:
        beds_available = h["beds_total"] - h["beds_occupied"]
        vents_available = h["ventilators_total"] - h["ventilators_in_use"]

        distance_km = haversine(
            ambulance_loc["lat"], ambulance_loc["lon"],
            h["latitude"], h["longitude"]
        )

        score -= distance_km * DISTANCE_WEIGHT

        if beds_available <= 0:
            score -= NO_BEDS_PENALTY
        if vents_available <= 0:
            score -= NO_VENTS_PENALTY

        bed_ratio = h["beds_occupied"] / float(h["beds_total"])
        vent_ratio = h["ventilators_in_use"] / float(h["ventilators_total"])

        if bed_ratio >= BED_THRESHOLD:
            score -= HIGH_BED_PENALTY
        if vent_ratio >= VENT_THRESHOLD:
            score -= HIGH_VENT_PENALTY
        if h["oxygen_percent"] <= OXYGEN_CRITICAL:
            score -= LOW_OXYGEN_PENALTY

        return round(score, 2), round(distance_km, 2)
    except Exception as e:
        print(f"Scoring error: {e}")
        return 0.0, 999.0


def generate_explanation(request, ranked_hospitals):
    """Generate AI explanation for referral recommendation."""
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
- Be concise and factual.
"""
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"LLM explanation failed: {e}")
        top = ranked_hospitals[0]
        return (
            f"{top['hospital_name']} is recommended: "
            f"{top['distance_km']}km away, "
            f"{top['beds_available']} beds and {top['ventilators_available']} ventilators available. "
            f"This referral is based on proximity and resource availability."
        )


def handle_referral(request):
    """Process a referral request and return recommendations."""
    hospitals = fetch_hospitals()

    if not hospitals:
        return {"error": "No hospitals available or database connection failed", "generated_at": datetime.utcnow().isoformat() + "Z"}

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

    ranked.sort(key=lambda x: x["score"], reverse=True)

    top_3 = ranked[:3]
    explanation = generate_explanation(request, top_3)

    return {
        "request_id": f"REF_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "recommendations": top_3,
        "all_hospitals_count": len(ranked),
        "explanation": explanation
    }


if __name__ == "__main__":
    test_conn = get_db_connection()
    if not test_conn:
        print("Cannot start: Database connection failed")
        exit(1)

    print("Database connection successful")
    test_conn.close()

    referral_request = {
        "patient_severity": "CRITICAL",
        "required_resource": "VENTILATOR",
        "ambulance_location": {"lat": 18.5204, "lon": 73.8567}
    }

    try:
        response = handle_referral(referral_request)
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error handling referral: {e}")
        traceback.print_exc()
