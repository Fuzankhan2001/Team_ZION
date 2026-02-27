from fastapi import APIRouter
from app.database import execute_query

router = APIRouter()


@router.get("/dashboard")
def get_dashboard():
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
def get_hospital_state(facility_id: str):
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


@router.get("/history/{facility_id}")
def get_hospital_history(facility_id: str):
    """Get resource history for graphs."""
    query = """
        SELECT beds_occupied, oxygen_percent, recorded_at
        FROM hospital_history
        WHERE facility_id = %s
        ORDER BY recorded_at DESC
        LIMIT 50
    """
    result = execute_query(query, (facility_id,))
    return result or []


@router.get("/admissions/{facility_id}")
def get_incoming_admissions(facility_id: str):
    """Get incoming admissions for a hospital."""
    query = """
        SELECT * FROM incoming_admissions
        WHERE hospital_id = %s AND status = 'EN_ROUTE'
        ORDER BY created_at DESC
    """
    result = execute_query(query, (facility_id,))
    return result or []
