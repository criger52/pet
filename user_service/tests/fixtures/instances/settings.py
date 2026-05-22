import pytest

from src.config import Settings, get_settings


@pytest.fixture
def settings() -> Settings:
    settings = get_settings()
    settings.USER_SERVICE_DB_URL = "postgresql+asyncpg://user:user@localhost:5433/user_test"
    return settings