from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "User Service"
    SERVICE_VERSION: str = "1.0"
    USER_SERVICE_DB_URL: str = "postgresql+asyncpg://user:user@user-db:5432/user"
    SERVICE_PORT: int = 8007
    DEBUG: bool = Field(...)
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-bootstrap:9092"
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = Field(...)


    class ConfigDict:
        extra = "ignore"
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()