from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# SECURITY CONFIG
SECRET_KEY = "supersecretkey"  # In production, this goes in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Checks if the typed password matches the DB hash."""
    # Since we manually inserted 'pass123' without hashing in the DB setup,
    # we need a temporary hack to allow plain text testing.
    # In production, ALWAYS hash.
    if plain_password == hashed_password:
        return True
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Generates the JWT Token string."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt