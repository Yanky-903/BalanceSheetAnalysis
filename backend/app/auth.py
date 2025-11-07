import os
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from .db import SessionLocal
from .models import User

# Use PBKDF2 (pure-python / hashlib) to avoid bcrypt native issues on macOS
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str):
    return pwd_ctx.hash(password)

def verify_password(plain, hashed):
    return pwd_ctx.verify(plain, hashed)

def create_access_token(data: dict, expires_hours=ACCESS_TOKEN_EXPIRE_HOURS):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token body")
    db = SessionLocal()
    user = db.query(User).filter(User.email == user_email).first()
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
