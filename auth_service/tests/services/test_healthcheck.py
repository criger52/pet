import pytest
from src.services.healthcheck import HealthCheckService


@pytest.mark.asyncio
async def test__healthcheck_service__ok(
        healthcheck_service: HealthCheckService,
) -> None:
    assert healthcheck_service.health_check()
