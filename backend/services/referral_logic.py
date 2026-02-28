import math
from app.database import execute_query

def haversine(lat1, lon1, lat2, lon2):
    """Calculates distance between two GPS points in km."""
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def find_best_hospitals(user_lat: float, user_lon: float, severity: str):
    """
    1. Fetches live data from DB.
    2. Scores hospitals based on Distance + Availability.
    3. Returns sorted list.
    """
    
    # 1. Fetch Live Data
    query = """
        SELECT 
            h.facility_id, h.name, h.latitude, h.longitude,
            s.beds_occupied, c.beds_total,
            s.ventilators_in_use, c.ventilators_total,
            s.oxygen_percent
        FROM hospitals h
        JOIN hospital_state s ON h.facility_id = s.facility_id
        JOIN hospital_capacity c ON h.facility_id = c.facility_id
    """
    hospitals = execute_query(query)
    
    ranked_results = []
    
    # 2. Score Each Hospital
    for h in hospitals:
        score = 100
        
        # Calculate Availability
        beds_avail = h['beds_total'] - h['beds_occupied']
        vents_avail = h['ventilators_total'] - h['ventilators_in_use']
        
        # Distance Calculation
        dist = haversine(user_lat, user_lon, h['latitude'], h['longitude'])
        
        # --- SCORING RULES ---
        score -= dist * 2  # Penalty for distance
        
        if beds_avail <= 0: score -= 50
        if vents_avail <= 0 and severity == 'CRITICAL': score -= 80
        if h['oxygen_percent'] < 30: score -= 40
        
        ranked_results.append({
            "id": h['facility_id'],
            "name": h['name'],
            "score": round(score, 1),
            "distance_km": round(dist, 1),
            "beds_available": beds_avail,
            "vents_available": vents_avail,
            # ADD THESE TWO LINES:
            "latitude": h['latitude'],
            "longitude": h['longitude']
        })
        
    # 3. Sort by Score (High to Low)
    ranked_results.sort(key=lambda x: x['score'], reverse=True)
    
    return ranked_results[:3]  # Return top 3