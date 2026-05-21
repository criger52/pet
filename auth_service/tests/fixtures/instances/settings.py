import pytest

from src.config import Settings, get_settings


@pytest.fixture
def settings() -> Settings:
    settings = get_settings()
    settings.DB_URL = "postgresql+asyncpg://auth:auth@localhost:5432/auth_test"
    return settings