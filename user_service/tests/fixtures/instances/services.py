import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.healthcheck import HealthCheckService
from src.services.user_service import UserProfileService


@pytest.fixture
async def healthcheck_service(
        session: AsyncSession,
) -> HealthCheckService:
    return HealthCheckService(session=session)

@pytest.fixture
async def user_service(
        session: AsyncSession,
) -> UserProfileService:
    return UserProfileService(session=session)
