from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import execute_query
from app.services.triage_engine import classify_severity
import math
import json
from datetime import datetime

router = APIRouter()


class ReferralRequest(BaseModel):
    patient_severity: str
    required_resource: str
    ambulance_lat: float
    ambulance_lon: float
    patient_id: Optional[str] = None
    vitals: Optional[dict] = None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.post("/request")
def request_referral(req: ReferralRequest):
    """Process a referral request from an ambulance."""

    # Get all hospitals with capacity
    hospitals = execute_query("""
        SELECT h.facility_id, h.name, h.latitude, h.longitude,
               s.beds_occupied, c.beds_total,
               s.ventilators_in_use, c.ventilators_total,
               s.oxygen_percent
        FROM hospitals h
        JOIN hospital_state s ON h.facility_id = s.facility_id
        JOIN hospital_capacity c ON h.facility_id = c.facility_id
        WHERE c.beds_total > 0
    """)

    if not hospitals:
        raise HTTPException(status_code=404, detail="No hospitals available")

    # Score each hospital
    scored = []
    for h in hospitals:
        score = 100
        dist = haversine(req.ambulance_lat, req.ambulance_lon, h['latitude'], h['longitude'])

        score -= dist * 1.5
        beds_avail = h['beds_total'] - h['beds_occupied']
        vents_avail = h['ventilators_total'] - h['ventilators_in_use']

        if beds_avail <= 0:
            score -= 40
        if vents_avail <= 0:
            score -= 50
        if h['oxygen_percent'] <= 30:
            score -= 30

        scored.append({
            "facility_id": h['facility_id'],
            "name": h['name'],
            "score": round(score, 2),
            "distance_km": round(dist, 2),
            "beds_available": beds_avail,
            "ventilators_available": vents_avail,
            "oxygen_percent": h['oxygen_percent'],
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    recommended = scored[0] if scored else None

    # Log referral
    request_id = f"REF_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    execute_query("""
        INSERT INTO ref_logs (request_id, patient_id, severity, required_resource,
                             ambulance_lat, ambulance_lon, recommended_hospital,
                             confidence_score, vitals)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        request_id, req.patient_id, req.patient_severity, req.required_resource,
        req.ambulance_lat, req.ambulance_lon,
        recommended['facility_id'] if recommended else None,
        recommended['score'] if recommended else 0,
        json.dumps(req.vitals) if req.vitals else None
    ))

    return {
        "request_id": request_id,
        "recommended": recommended,
        "alternatives": scored[1:3],
        "severity_class": classify_severity(req.patient_severity),
    }
