from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.broker.producer import KafkaProducer
from src.services.healthcheck import HealthCheckService
from src.services.login import LoginService
from src.services.register import RegisterService


@pytest.fixture
async def healthcheck_service(
        session: AsyncSession,
) -> HealthCheckService:
    return HealthCheckService(session=session)

@pytest.fixture
async def register_service(
        session: AsyncSession,
) -> RegisterService:
    return RegisterService(session=session, kafka_producer=AsyncMock(KafkaProducer))


@pytest.fixture
async def login_service(
        session: AsyncSession,
        settings,
) -> LoginService:
    return LoginService(session=session, settings=settings)
