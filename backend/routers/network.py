from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import execute_query
from app.services.auth_dependency import get_current_user

router = APIRouter()

class NetworkMessage(BaseModel):
    message: str
    type: str = "CHAT"
    sender_name: str = None 

@router.get("/messages")
def get_network_messages(current_user: dict = Depends(get_current_user)):
    """
    Fetch the LAST 50 messages (Newest ones).
    We select them DESC (newest first) then sort ASC (oldest first) so the chat reads correctly.
    """
    query = """
        SELECT * FROM (
            SELECT * FROM hospital_network_messages 
            ORDER BY created_at DESC 
            LIMIT 50
        ) AS sub
        ORDER BY created_at ASC;
    """
    return execute_query(query)

@router.post("/message")
def post_network_message(msg: NetworkMessage, current_user: dict = Depends(get_current_user)):
    
    sender_name = msg.sender_name if msg.sender_name else current_user.get("hospital_name", current_user["facility_id"])
    
    # 1. INSERT 
    insert_query = """
        INSERT INTO hospital_network_messages (sender_id, sender_name, message_text, message_type)
        VALUES (%s, %s, %s, %s)
    """
    result = execute_query(insert_query, (current_user["facility_id"], sender_name, msg.message, msg.type), commit=True)
    
    if result is None:
        raise HTTPException(status_code=500, detail="Database Insert Failed")

    # 2. FETCH the saved message
    fetch_query = """
        SELECT * FROM hospital_network_messages 
        WHERE sender_id = %s 
        ORDER BY created_at DESC 
        LIMIT 1
    """
    saved_message = execute_query(fetch_query, (current_user["facility_id"],), fetch_one=True)

    # 3. AI Logic
    text = msg.message.lower()
    auto_reply = None

    if "vent" in text:
        res = execute_query("SELECT name, ventilators_available FROM hospital_live_dashboard WHERE ventilators_available > 0 ORDER BY ventilators_available DESC LIMIT 1", fetch_one=True)
        if res: auto_reply = f"System: Network Scan indicates {res['name']} has {res['ventilators_available']} ventilators available."
    elif "bed" in text or "icu" in text or "capacity" in text:
        res = execute_query("SELECT name, beds_available FROM hospital_live_dashboard WHERE beds_available > 0 ORDER BY beds_available DESC LIMIT 1", fetch_one=True)
        if res: auto_reply = f"System: Capacity Check - {res['name']} reports {res['beds_available']} open beds."
    elif "oxygen" in text or "o2" in text:
        res = execute_query("SELECT name, oxygen_percent FROM hospital_live_dashboard WHERE oxygen_percent > 90 ORDER BY oxygen_percent DESC LIMIT 1", fetch_one=True)
        if res: auto_reply = f"System: {res['name']} reports optimal oxygen reserves ({res['oxygen_percent']}%)."

    if auto_reply:
        execute_query(insert_query, ('SYSTEM', 'AI COORDINATOR', auto_reply, 'AUTO_REPLY'), commit=True)

    if saved_message:
        return saved_message
        
    raise HTTPException(status_code=500, detail="Message saved but verification failed")