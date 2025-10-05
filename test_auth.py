import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.user import User
from app.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register():
    response = client.post("/auth/register", json={"username": "testuser", "email": "test@example.com", "password": "testpass"})
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}


def test_login():
    # First register
    client.post("/auth/register", json={"username": "testuser2", "email": "test2@example.com", "password": "testpass"})
    response = client.post("/auth/login", data={"username": "testuser2", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_me():
    # Register and login
    client.post("/auth/register", json={"username": "testuser3", "email": "test3@example.com", "password": "testpass"})
    login_response = client.post("/auth/login", data={"username": "testuser3", "password": "testpass"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser3"