from datetime import datetime, timedelta
from typing import Optional

import jwt
import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

redis_client = redis.from_url(settings.redis_url)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    print("Hashing password...", password)
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    # Store token in Redis with expiration
    user_id = data.get("sub")
    if user_id:
        redis_client.setex(f"token:{user_id}", settings.access_token_expire_minutes * 60, encoded_jwt)

    return encoded_jwt


def verify_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check if token exists in Redis (means it's still valid)
    stored_token = redis_client.get(f"token:{username}")
    if not stored_token or stored_token.decode() != token:
        raise HTTPException(status_code=401, detail="Token has been invalidated")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    return verify_token(token, db)


def invalidate_token(token: str):
    # This function is no longer needed with the new token management approach
    pass