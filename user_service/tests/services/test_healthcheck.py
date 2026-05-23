from unittest.mock import AsyncMock, patch

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.healthcheck import HealthCheckService


async def test__healthcheck_service__check__ok(
        healthcheck_service: HealthCheckService,
) -> None:
    assert await healthcheck_service.health_check()


async def test__healthcheck_service__check__db_error(
        session: AsyncSession,
) -> None:
    service = HealthCheckService(session=session)
    with patch.object(session, "execute", AsyncMock(side_effect=SQLAlchemyError("db down"))):
        assert await service.health_check() is False
