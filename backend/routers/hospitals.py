from fastapi import APIRouter, Depends, HTTPException
from app.database import execute_query
from app.services.auth_dependency import get_current_user
from app.services.triage_engine import evaluate_hospital_risk 
import datetime

router = APIRouter()

# --- EXISTING HELPER (Keep this) ---
def generate_risk_alerts(stats):
    alerts = []
    
    # 1. Bed Logic
    bed_util = stats["beds_utilization_percent"]
    if bed_util >= 90:
        alerts.append({"level": "CRITICAL", "message": "Hospital is at MAX CAPACITY. Divert ambulances immediately."})
    elif bed_util >= 80:
        alerts.append({"level": "WARNING", "message": "High Bed Occupancy (>80%). Prepare overflow protocols."})
        
    # 2. Ventilator Logic
    vent_util = stats["vent_utilization_percent"]
    if vent_util >= 90:
        alerts.append({"level": "CRITICAL", "message": "Ventilators critically low. Request external supply."})
    elif vent_util >= 80:
        alerts.append({"level": "WARNING", "message": "Ventilator usage high. Monitor critical patients closely."})
        
    # 3. Oxygen Logic
    oxy_level = stats["oxygen_percent"]
    if oxy_level < 20:
        alerts.append({"level": "CRITICAL", "message": "OXYGEN CRITICAL (<20%). IMMEDIATE REFILL NEEDED."})
    elif oxy_level < 50:
        alerts.append({"level": "WARNING", "message": "Oxygen reserves low. Schedule refill."})
        
    return alerts

# --- ENDPOINTS ---

@router.get("/dashboard")
def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    user_role = current_user["role"]
    facility_id = current_user["facility_id"]
    
    if user_role != "hospital_admin":
        raise HTTPException(status_code=403, detail="Not authorized to view hospital dashboard")
    
    query = "SELECT * FROM hospital_live_dashboard WHERE facility_id = %s"
    result = execute_query(query, (facility_id,), fetch_one=True)
    
    if not result:
        raise HTTPException(status_code=404, detail="Hospital data not found")
    
    active_alerts = generate_risk_alerts(result)
        
    return {
        "status": "success",
        "hospital_name": result["name"],
        "facility_id": facility_id, 
        "last_updated": result["last_updated"],
        "data": {
            "beds": {
                "total": result["beds_total"],
                "occupied": result["beds_occupied"],
                "available": result["beds_available"],
                "utilization": result["beds_utilization_percent"]
            },
            "ventilators": {
                "total": result["ventilators_total"],
                "in_use": result["ventilators_in_use"],
                "available": result["ventilators_available"],
                "utilization": result["vent_utilization_percent"]
            },
            "oxygen": {
                "percent": result["oxygen_percent"],
                "status": result["oxygen_status"]
            }
        },
        "alerts": active_alerts
    }

@router.get("/resources")
def get_hospital_resources(current_user: dict = Depends(get_current_user)):
    facility_id = current_user["facility_id"]
    query = """
        SELECT resource_id, current_value, updated_at 
        FROM hospital_resources 
        WHERE facility_id = %s AND resource_type = 'OXYGEN'
        ORDER BY resource_id ASC
    """
    cylinders = execute_query(query, (facility_id,))
    
    formatted_cylinders = []
    if cylinders:
        for cyl in cylinders:
            percent = min(100, max(0, (cyl['current_value'] / 2000) * 100))
            formatted_cylinders.append({
                "id": cyl['resource_id'],
                "pressure": cyl['current_value'],
                "percent": round(percent, 1),
                "status": "NORMAL" if percent > 30 else "LOW"
            })
        
    return {"oxygen_cylinders": formatted_cylinders}

@router.get("/history")
def get_hospital_history(current_user: dict = Depends(get_current_user)):
    facility_id = current_user["facility_id"]
    query = """
        SELECT recorded_at, beds_occupied, oxygen_percent 
        FROM hospital_history 
        WHERE facility_id = %s 
        ORDER BY recorded_at DESC 
        LIMIT 50
    """
    history = execute_query(query, (facility_id,))
    return {"history": history[::-1] if history else []}

@router.get("/{hospital_id}/triage")
def get_triage_status(hospital_id: str):
    """
    Calculates Triage Status based on REAL DB HISTORY.
    """
    # 1. Fetch Static Capacities & Current Vents
    cap_query = """
        SELECT beds_total, ventilators_total, ventilators_in_use
        FROM hospital_live_dashboard 
        WHERE facility_id = %s
    """
    capacity_data = execute_query(cap_query, (hospital_id,), fetch_one=True)
    
    if not capacity_data:
        return {"status": "ERROR", "message": "Hospital ID not found"}

    # 2. Fetch Historical Trends (Last 20 records)
    # FIX: Fetch DESC (Newest) then reverse list
    hist_query = """
        SELECT recorded_at, beds_occupied, oxygen_percent
        FROM hospital_history
        WHERE facility_id = %s
        ORDER BY recorded_at DESC
        LIMIT 20
    """
    history_rows = execute_query(hist_query, (hospital_id,))
    
    # REVERSE HERE so the Engine processes Oldest -> Newest
    if history_rows:
        history_rows = history_rows[::-1]

    # 3. Handle Insufficient Data
    if not history_rows or len(history_rows) < 2:
        return {
            "hospital_id": hospital_id,
            "prediction": {
                "status": "STABLE", 
                "color": "green",
                "message": "Collecting data...",
                "hours_remaining": 999
            },
            "timestamp": datetime.datetime.now()
        }

    # 4. Format Data for the Engine
    oxygen_data = []
    bed_data = []
    vent_data = []
    
    current_vent_usage = capacity_data.get('ventilators_in_use', 0)

    for row in history_rows:
        ts = row['recorded_at']
        oxygen_data.append({'timestamp': ts, 'value': row['oxygen_percent']})
        bed_data.append({'timestamp': ts, 'value': row['beds_occupied']})
        vent_data.append({'timestamp': ts, 'value': current_vent_usage})

    # 5. Run the Triage Engine
    risk_assessment = evaluate_hospital_risk(
        oxygen_data, 
        bed_data, 
        vent_data, 
        total_beds=capacity_data['beds_total'], 
        total_vents=capacity_data['ventilators_total']
    )
    
    return {
        "hospital_id": hospital_id,
        "prediction": risk_assessment['primary_alert'], 
        "all_risks": risk_assessment['details'],        
        "timestamp": datetime.datetime.now()
    }

@router.get("/{hospital_id}/incoming")
def get_incoming_ambulances(hospital_id: str):
    query = """
        SELECT * FROM incoming_admissions 
        WHERE hospital_id = %s AND status = 'EN_ROUTE'
        ORDER BY created_at DESC
    """
    incoming = execute_query(query, (hospital_id,))
    return incoming if incoming else []

@router.post("/{admission_id}/acknowledge")
def acknowledge_admission(admission_id: int):
    query = "UPDATE incoming_admissions SET status = 'ADMITTED' WHERE id = %s"
    execute_query(query, (admission_id,), commit=True)
    return {"status": "success", "message": "Patient admitted"}