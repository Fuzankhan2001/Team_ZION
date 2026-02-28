from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.auth_dependency import get_current_user
from app.services.chat_service import process_chat_message

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    mode: str = "NORMAL"
    triage_context: Optional[Dict[str, Any]] = None # <--- NEW FIELD

@router.post("/ask")
def ask_hospital_ai(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_role = current_user["role"]
    facility_id = current_user["facility_id"]
    
    if user_role != "hospital_admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Pass everything to the service
    response_text = process_chat_message(
        request.message, 
        facility_id, 
        request.mode, 
        request.triage_context
    )
    
    return {"response": response_text}