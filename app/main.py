from fastapi import FastAPI
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import user
from app.routes.auth import router as auth_router

Base.metadata.create_all(bind=engine)

# Security scheme for Swagger UI
security = HTTPBearer()

app = FastAPI(
    title="FastAPI JWT Authentication",
    description="JWT + Redis hybrid authentication with PostgreSQL",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "FastAPI app with JWT + Redis hybrid auth"}