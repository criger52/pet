
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.healthcheck import HealthCheckService
from src.services.login import LoginService
from src.services.outbox import OutBoxService
from src.services.register import RegisterService
from src.services.saga import SagaService


@pytest.fixture
async def healthcheck_service(
        session: AsyncSession,
) -> HealthCheckService:
    return HealthCheckService(session=session)


@pytest.fixture
async def outbox_service(
) -> OutBoxService:
    return OutBoxService()

@pytest.fixture
async def register_service(
        session: AsyncSession,
        outbox_service
) -> RegisterService:
    return RegisterService(session=session, outbox_service=outbox_service)


@pytest.fixture
async def login_service(
        session: AsyncSession,
        settings,
) -> LoginService:
    return LoginService(session=session, settings=settings)

@pytest.fixture
async def saga_service(
        async_session_maker,
) -> SagaService:
    return SagaService(session_factory=async_session_maker)
