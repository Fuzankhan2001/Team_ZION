import numpy as np
from sklearn.linear_model import LinearRegression
import datetime

def calculate_slope(data):
    """
    Calculates the rate of change (slope) per hour.
    Input: list of {'timestamp': datetime, 'value': float}
    """
    if not data or len(data) < 2:
        return 0.0

    # Convert timestamps to hours relative to the start
    start_time = data[0]['timestamp']
    X = np.array([(d['timestamp'] - start_time).total_seconds() / 3600 for d in data]).reshape(-1, 1)
    y = np.array([d['value'] for d in data])

    model = LinearRegression()
    model.fit(X, y)
    
    return model.coef_[0] # Change per hour

def evaluate_hospital_risk(oxygen_data, bed_data, vent_data, total_beds, total_vents):
    """
    Analyzes trends to predict failures.
    Returns a dict with 'primary_alert' and 'details'.
    """
    
    # 1. Calculate Slopes (Drain Rates)
    oxy_slope = calculate_slope(oxygen_data)
    bed_slope = calculate_slope(bed_data)
    
    # Get latest values
    current_oxy = oxygen_data[-1]['value'] if oxygen_data else 0
    current_beds = bed_data[-1]['value'] if bed_data else 0
    
    # 2. PREDICT OXYGEN FAILURE
    oxy_hours_left = 999.0 # Default "Safe"
    if oxy_slope < -0.1: # If draining significantly
        # Time = Current / Rate
        oxy_hours_left = current_oxy / abs(oxy_slope)
    
    # 3. DETERMINE STATUS & MESSAGE
    status = "STABLE"
    message = "Systems operating within normal parameters."
    
    # A. CRITICAL LOGIC (Red)
    if oxy_hours_left < 4:
        status = "CRITICAL"
        message = f"CRITICAL: Oxygen failure in {oxy_hours_left:.1f} hrs (Draining at {abs(oxy_slope):.1f}%/hr)"
    elif current_oxy < 20:
        status = "CRITICAL"
        message = "CRITICAL: Oxygen levels critically low (<20%)."
    elif current_beds >= total_beds:
        status = "CRITICAL"
        message = "CRITICAL: Bed capacity reached 100%. Divert protocol recommended."
        
    # B. WARNING LOGIC (Yellow)
    elif oxy_hours_left < 12:
        status = "WARNING"
        message = f"WARNING: Oxygen trend unstable. Empty in {oxy_hours_left:.1f} hrs."
    elif current_beds >= (total_beds * 0.9):
        status = "WARNING"
        message = "WARNING: Bed occupancy > 90%."
        
    # 4. CONSTRUCT RESULT
    # FIX: We explicitly add 'hours_remaining' here so the Chatbot can read it
    primary_alert = {
        "status": status,
        "message": message,
        "hours_remaining": round(oxy_hours_left, 1), # <--- THIS WAS MISSING OR CALCULATED WRONG
        "drain_rate": round(oxy_slope, 2)
    }

    return {
        "primary_alert": primary_alert,
        "details": {
            "oxygen_trend": round(oxy_slope, 2),
            "bed_trend": round(bed_slope, 2)
        }
    }