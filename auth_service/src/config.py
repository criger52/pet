from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AUTH_SERVICE_NAME: str = "Auth Service"
    AUTH_SERVICE_VERSION: str = "1.0"
    AUTH_DB_URL: str = "postgresql+asyncpg://auth:auth@auth-db:5432/auth"
    AUTH_SERVICE_PORT: int = 8000
    AUTH_DEBUG: bool = True

    class ConfigDict:
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()