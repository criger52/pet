from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    USER_SERVICE_NAME: str = "User Service"
    USER_SERVICE_VERSION: str = "1.0"
    USER_DB_URL: str = "postgresql+asyncpg://user:user@user-db:5432/user"
    USER_SERVICE_PORT: int = 8007
    USER_DEBUG: bool = True

    class ConfigDict:
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()