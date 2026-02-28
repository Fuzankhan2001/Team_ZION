from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.services.auth_utils import SECRET_KEY, ALGORITHM

# This tells FastAPI that the token comes from the "/auth/token" url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validates the token and returns the user info inside it.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        facility_id: str = payload.get("facility_id")
        
        if username is None:
            raise credentials_exception
            
        return {"username": username, "role": role, "facility_id": facility_id}
        
    except JWTError:
        raise credentials_exception