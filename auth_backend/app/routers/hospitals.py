from fastapi import APIRouter, Depends
from app.database import execute_query
from app.services.auth_dependency import get_current_user

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(current_user: dict = Depends(get_current_user)):
    """Get live dashboard data for all hospitals."""
    query = """
        SELECT 
            h.facility_id, h.name, h.city,
            s.beds_occupied, c.beds_total,
            s.ventilators_in_use, c.ventilators_total,
            s.oxygen_percent, s.oxygen_status
        FROM hospitals h
        JOIN hospital_state s ON h.facility_id = s.facility_id
        JOIN hospital_capacity c ON h.facility_id = c.facility_id
    """
    result = execute_query(query)
    return result or []


@router.get("/state/{facility_id}")
def get_hospital_state(facility_id: str, current_user: dict = Depends(get_current_user)):
    """Get state of a specific hospital."""
    query = """
        SELECT 
            h.facility_id, h.name,
            s.beds_occupied, c.beds_total,
            s.ventilators_in_use, c.ventilators_total,
            s.oxygen_percent, s.oxygen_status,
            s.last_updated
        FROM hospitals h
        JOIN hospital_state s ON h.facility_id = s.facility_id
        JOIN hospital_capacity c ON h.facility_id = c.facility_id
        WHERE h.facility_id = %s
    """
    result = execute_query(query, (facility_id,), fetch_one=True)
    return result or {}
