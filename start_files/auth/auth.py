# keytech/auth/auth.py
from datetime import datetime, timedelta
from jose import jwt
from start_files.config import SECRET_KEY  # <-- use this

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # JWT expects a timestamp, not datetime
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
