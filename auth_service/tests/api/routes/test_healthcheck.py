from http import HTTPStatus

from httpx import AsyncClient

from src.api.schemas.health import HealthSchema


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