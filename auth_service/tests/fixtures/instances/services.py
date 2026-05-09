import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.healthcheck import HealthCheckService


@pytest.fixture
async def healthcheck_service(
        session: AsyncSession,
) -> HealthCheckService:
    return HealthCheckService(session=session)
