from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "Auth Service"
    SERVICE_VERSION: str = "1.0"
    DB_URL: str = "postgresql+asyncpg://auth:auth@auth-db:5432/auth"
    SERVICE_PORT: int = 8000
    DEBUG: bool = True

    class ConfigDict:
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()