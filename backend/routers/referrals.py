from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.referral_logic import find_best_hospitals

router = APIRouter()

# Define the Input Format (Validation)
class ReferralRequest(BaseModel):
    latitude: float
    longitude: float
    severity: str  # "NORMAL" or "CRITICAL"

@router.post("/recommend")
def get_recommendation(request: ReferralRequest):
    """
    Endpoint for Ambulances.
    Input: {lat, lon, severity}
    Output: Top 3 Hospitals
    """
    try:
        results = find_best_hospitals(request.latitude, request.longitude, request.severity)
        return {"status": "success", "recommendations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))