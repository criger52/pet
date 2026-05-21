from http import HTTPStatus
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.api.schemas.health import HealthSchema
from src.services.healthcheck import HealthCheckService


API_URL = "api/v1/auth/"

async def test__healthcheck__status__ok(
        client: AsyncClient,
):
    result = await client.get(
        f"{API_URL}health",
    )

    assert result.status_code == HTTPStatus.OK


async def test__healthcheck__response__ok(
        client: AsyncClient,
):
    result = await client.get(
        f"{API_URL}health",
    )

    assert result.json() == HealthSchema(is_alive=True).model_dump()


async def test__healthcheck__status__unavailable(
        client: AsyncClient,
):
    with patch.object(
        HealthCheckService,
        "health_check",
        AsyncMock(return_value=False),
    ):
        result = await client.get(f"{API_URL}health")

    assert result.status_code == HTTPStatus.SERVICE_UNAVAILABLE