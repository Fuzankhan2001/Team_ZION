from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.database import execute_query
from app.services.auth_utils import verify_password, create_access_token

router = APIRouter()

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Standard Login Endpoint.
    Input: username, password
    Output: {access_token, token_type, role, facility_id}
    """
    
    # 1. Fetch User from DB
    query = "SELECT * FROM users WHERE username = %s"
    user = execute_query(query, (form_data.username,), fetch_one=True)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username")
    
    # 2. Check Password
    if not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # 3. Create Token
    # We embed the role and facility_id inside the token
    token_data = {
        "sub": user['username'],
        "role": user['role'],
        "facility_id": user['facility_id']
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user['role'],
        "facility_id": user['facility_id']
    }