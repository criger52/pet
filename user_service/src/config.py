from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "User Service"
    SERVICE_VERSION: str = "1.0"
    DB_URL: str = "postgresql+asyncpg://user:user@user-db:5432/user"
    SERVICE_PORT: int = 8007
    DEBUG: bool = True

    class ConfigDict:
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()