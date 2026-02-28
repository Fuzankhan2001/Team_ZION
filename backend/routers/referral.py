from fastapi import APIRouter
from pydantic import BaseModel
import math
import json
import os
import uuid
from groq import Groq
from app.database import execute_query
import httpx # You might need to pip install httpx
from datetime import datetime
from dotenv import load_dotenv

router = APIRouter()

# Get the API key securely
api_key = os.getenv("GROQ_API_KEY")
# Initialize the Groq client
client = Groq(api_key=api_key)

# --- CONFIG ---
DISTANCE_WEIGHT = 1.5
BED_WEIGHT = 2.0
RISK_PENALTY_WARNING = 15.0  
RISK_PENALTY_CRITICAL = 50.0 

# --- DATA MODELS ---
class AmbulanceLocation(BaseModel):
    lat: float
    lon: float

class PatientVitals(BaseModel):
    spo2: int
    systolic_bp: int
    heart_rate: int
    resp_rate: int
    gcs: int

class ReferralRequest(BaseModel):
    patient_id: str
    # severity: str  <-- REMOVED (Calculated automatically now)
    vitals: PatientVitals # <-- ADDED
    required_resource: str 
    ambulance_location: AmbulanceLocation

class NotificationRequest(BaseModel):
    patient_id: str
    facility_id: str
    severity: str
    required_resource: str
    ambulance_id: str
    vitals: PatientVitals

# --- HELPER: MEWS CALCULATOR (Your Logic) ---
def calculate_severity(vitals: dict):
    """
    Categorizes patient condition based on 5 major vitals.
    """
    # 1. CRITICAL TRIGGERS
    if (vitals['spo2'] < 90 or
        vitals['systolic_bp'] < 90 or vitals['systolic_bp'] > 180 or
        vitals['heart_rate'] < 50 or vitals['heart_rate'] > 130 or
        vitals['resp_rate'] < 10 or vitals['resp_rate'] > 30 or
        vitals['gcs'] <= 11):
        return "CRITICAL"

    # 2. MODERATE TRIGGERS
    if (vitals['spo2'] <= 94 or
        vitals['systolic_bp'] < 100 or vitals['systolic_bp'] >= 141 or
        vitals['heart_rate'] < 60 or vitals['heart_rate'] > 100 or
        vitals['resp_rate'] > 20 or
        vitals['gcs'] < 15):
        return "MODERATE"

    # 3. OTHERWISE NORMAL
    return "NORMAL"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371 
    d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def save_decision_log(data):
    # Format Postgres Array
    alts = "{" + ",".join(data['alternatives']) + "}"
    
    # Dump Vitals to JSON string
    vitals_json = json.dumps(data['patient']['vitals'])

    # UPDATED QUERY: Now includes 'vitals' column
    query = """
        INSERT INTO ref_logs (
            request_id, patient_id, severity, required_resource, 
            ambulance_lat, ambulance_lon, recommended_hospital, 
            alternatives, confidence_score, ai_reasoning, vitals
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    
    execute_query(query, (
        data['request_id'], data['patient']['patient_id'], 
        data['calculated_severity'], # Use the calculated one
        data['patient']['required_resource'],
        data['patient']['ambulance_location']['lat'], 
        data['patient']['ambulance_location']['lon'], 
        data['recommended'], alts, 
        data['confidence'], data['reasoning'],
        vitals_json # Save raw numbers for audit
    ), fetch_one=True)

# backend/routers/referral.py

# backend/routers/referral.py

def log_incoming_admission(data):
    # Convert vitals dict to JSON string if needed, or rely on psycopg2 to handle JSONB
    # We pass data.vitals directly
    import json
    vitals_json = json.dumps(data.vitals.dict())
    
    query = """
        INSERT INTO incoming_admissions 
        (ambulance_id, hospital_id, patient_id, severity, required_resource, status, vitals)
        VALUES (%s, %s, %s, %s, %s, 'EN_ROUTE', %s)
        RETURNING id;
    """
    try:
        execute_query(query, (
            data.ambulance_id, data.facility_id, data.patient_id, 
            data.severity, data.required_resource, vitals_json
        ), fetch_one=True, commit=True) # Ensure commit=True is passed/handled
    except Exception as e:
        print(f"CRITICAL DB ERROR: {e}")

# --- MAIN ENDPOINT ---
@router.post("/optimize")
async def optimize_referral(request: ReferralRequest):
    
    # 1. CALCULATE SEVERITY (The New Brain)
    # We convert the Pydantic model to a dict for your function
    vitals_dict = request.vitals.dict()
    severity_status = calculate_severity(vitals_dict)
    
    # 2. FETCH CANDIDATES
    sql = """
        SELECT 
            h.facility_id, h.name, h.latitude, h.longitude,
            (c.beds_total - s.beds_occupied) as beds_avail,
            (c.ventilators_total - s.ventilators_in_use) as vents_avail,
            CASE 
                WHEN (s.beds_occupied::float / NULLIF(c.beds_total,0)) > 0.9 THEN 'CRITICAL'
                WHEN (s.beds_occupied::float / NULLIF(c.beds_total,0)) > 0.8 THEN 'WARNING'
                ELSE 'NORMAL'
            END as risk_level
        FROM hospitals h
        JOIN hospital_state s ON h.facility_id = s.facility_id
        JOIN hospital_capacity c ON h.facility_id = c.facility_id
    """
    rows = execute_query(sql)
    
    candidates = []
    p_lat = request.ambulance_location.lat
    p_lon = request.ambulance_location.lon
    
    for row in rows:
        if request.required_resource == "VENTILATOR" and row['vents_avail'] <= 0: continue
        if row['beds_avail'] <= 0: continue
            
        dist = haversine(p_lat, p_lon, row['latitude'], row['longitude'])
        candidates.append({
            "facility_id": row['facility_id'],
            "name": row['name'],
            "latitude": row['latitude'],
            "longitude": row['longitude'],
            "distance_km": round(dist, 2),
            "beds_available": row['beds_avail'],
            "vents_available": row['vents_avail'],
            "risk_level": row['risk_level']
        })

    if not candidates:
        return {"status": "error", "message": "No hospitals found."}

    # 3. SCORE CANDIDATES
    scored = []
    for h in candidates:
        score = 100.0
        score -= (h["distance_km"] * DISTANCE_WEIGHT)
        score += (h["beds_available"] * BED_WEIGHT)
        if h["risk_level"] == "WARNING": score -= RISK_PENALTY_WARNING
        if h["risk_level"] == "CRITICAL": score -= RISK_PENALTY_CRITICAL
        h["algo_score"] = round(score, 2)
        scored.append(h)

    top_3 = sorted(scored, key=lambda x: x["algo_score"], reverse=True)[:3]

    # 4. AI REASONING (Updated Prompt)
    prompt = f"""
    Role: Medical Logistics Commander.
    Patient Status: {severity_status} (Calculated from Vitals: {vitals_dict}).
    Resource Needed: {request.required_resource}.
    Options: {json.dumps(top_3[:2])}
    
    Task: Pick best hospital.
    - If Status is CRITICAL: Prioritize Distance (Time is life).
    - If Status is STABLE/MODERATE: Prioritize Capacity/Quality.
    
    Return JSON: {{ "recommended_id": "ID", "reasoning": "Explanation citing vitals", "confidence": 0.9 }}
    """
    
    try:
        chat = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.1
        )
        ai_dec = json.loads(chat.choices[0].message.content)
    except:
        ai_dec = {"recommended_id": top_3[0]['facility_id'], "reasoning": "Fallback Algorithm", "confidence": 0.5}

    # 5. SAVE & RETURN
    req_id = uuid.uuid4().hex[:8]
    log_data = {
        "request_id": req_id,
        "patient": request.dict(),
        "calculated_severity": severity_status, # Pass this down
        "recommended": ai_dec['recommended_id'],
        "alternatives": [h['facility_id'] for h in top_3 if h['facility_id'] != ai_dec['recommended_id']],
        "confidence": ai_dec.get('confidence', 0.8),
        "reasoning": ai_dec.get('reasoning', "Algorithmic")
    }
    save_decision_log(log_data)

    return {
        "status": "success",
        "severity_assessed": severity_status, # Return calculated status to frontend
        "recommendation": next(h for h in top_3 if h['facility_id'] == ai_dec['recommended_id']),
        "alternatives": [h for h in top_3 if h['facility_id'] != ai_dec['recommended_id']],
        "ai_analysis": ai_dec
    }

# --- UPDATED NOTIFY ENDPOINT ---
@router.post("/notify")
async def notify_hospital_webhook(data: NotificationRequest):
    """
    1. Saves to DB (for Hospital Dashboard).
    2. Proxies to n8n (for WhatsApp).
    """
    
    # 1. SAVE TO DB (The New Part)
    try:
        log_incoming_admission(data)
        db_status = "Saved to Dashboard"
    except Exception as e:
        print(f"DB Log Error: {e}")
        db_status = "DB Save Failed"

    # 2. SEND TO WHATSAPP (Existing Logic)
    n8n_payload = {
        "event_type": "PATIENT_COMMITTED",
        "patient_id": data.patient_id,
        "facility_id": data.facility_id,
        "severity": data.severity,
        "required_resource": data.required_resource,
        "ambulance_id": data.ambulance_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    webhook_url = "http://127.0.0.1:5678/webhook-test/patient-commit"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=n8n_payload)
            
        if response.status_code == 200:
            return {"status": "success", "message": f"Hospital Notified ({db_status})"}
        else:
            return {"status": "error", "message": f"n8n returned {response.status_code}"}
            
    except Exception as e:
        print(f"Webhook Error: {e}")
        return {"status": "error", "message": "Failed to reach automation server"}