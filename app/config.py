from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    redis_url: str = "redis://localhost:6379"

    # PostgreSQL Database Configuration
    postgres_server: str = "postgres"  # Docker service name
    postgres_port: int = 5432
    postgres_database: str = "fastapi_db"
    postgres_username: str = "fastapi_user"
    postgres_password: str = "fastapi_password"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_username}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_database}"

    class Config:
        env_file = ".env"


settings = Settings()