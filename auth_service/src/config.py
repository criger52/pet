from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "Auth Service"
    SERVICE_VERSION: str = "1.0"
    AUTH_SERVICE_DB_URL: str = "postgresql+asyncpg://auth:auth@auth-db:5432/auth"
    SERVICE_PORT: int = 8000
    DEBUG: bool = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 360
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = Field(...)
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-broker:9092"

    class ConfigDict:
        extra = "ignore"

def get_settings() -> Settings:
    return Settings()