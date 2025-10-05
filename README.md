# FastAPI JWT + Redis Hybrid Authentication

This is a FastAPI application implementing user authentication with a hybrid approach combining JWT tokens and Redis session caching. When user permissions are changed, all access tokens for that user are immediately invalidated.

## Features

- User registration and login
- JWT token-based authentication
- Redis caching for session management
- Immediate token invalidation on permission changes
- Role-based access control (user/admin)
- PostgreSQL database support

## Installation & Running

### Configuration

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Update `.env` if you want to customize database settings (optional - defaults are set for Docker):
```env
POSTGRES_DATABASE=your-custom-db-name
POSTGRES_USERNAME=your-username
POSTGRES_PASSWORD=your-password
```

### Option 1: Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start PostgreSQL and Redis servers locally, or use Docker:
```bash
# Using Docker for databases
docker run -d --name postgres -e POSTGRES_DB=fastapi_db -e POSTGRES_USER=fastapi_user -e POSTGRES_PASSWORD=fastapi_password -p 5432:5432 postgres:15-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

### Option 2: Docker (Recommended)

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the application at `http://localhost:8000`
3. API documentation at `http://localhost:8000/docs`

## Database Setup

The application will automatically create tables when first run. PostgreSQL service is included in docker-compose.yml with default credentials.

## API Endpoints

- `POST /auth/login` - Login with username/password
- `POST /auth/register` - Register a new user
- `GET /auth/me` - Get current user info (requires auth)
- `POST /auth/change-role` - Change user role (admin only)
- `POST /auth/logout` - Logout (placeholder)

## How it works

- JWT tokens are issued on login
- Redis stores invalidated tokens and user permission change flags
- On each request, the token is validated against JWT and checked in Redis for invalidation
- When permissions change, a flag is set in Redis to invalidate all user tokens immediately