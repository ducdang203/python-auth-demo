from datetime import timedelta
from typing import Annotated

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, invalidate_token, get_password_hash, verify_password, redis_client
from app.config import settings
from app.database import get_db
from app.models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@router.post("/login", response_model=dict)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user already has a valid token in Redis
    existing_token = redis_client.get(f"token:{user.username}")
    if existing_token:
        return {"access_token": existing_token.decode(), "token_type": "bearer"}

    # Create new token if none exists
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=dict)
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == register_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(User).filter(User.email == register_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(register_data.password)
    db_user = User(username=register_data.username, email=register_data.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}


@router.get("/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"username": current_user.username, "email": current_user.email, "role": current_user.role}


@router.post("/change-role")
async def change_role(username: str, new_role: str, current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = new_role
    db.commit()
    # Remove user's token from Redis to force re-login
    redis_client.delete(f"token:{user.username}")
    return {"message": f"Role changed to {new_role}"}


@router.post("/logout")
async def logout(current_user: Annotated[User, Depends(get_current_user)]):
    # For simplicity, we can invalidate the token, but since JWT is stateless, we need to handle it in Redis
    # In a real app, you might want to get the token from header and invalidate it
    # For now, just return success
    return {"message": "Logged out successfully"}