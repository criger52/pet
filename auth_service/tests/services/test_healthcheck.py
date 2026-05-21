from src.services.healthcheck import HealthCheckService


async def test__healthcheck_service__check__ok(
        healthcheck_service: HealthCheckService,
) -> None:
    assert await healthcheck_service.health_check()
