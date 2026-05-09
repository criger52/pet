from http import HTTPStatus

from httpx import AsyncClient

from auth_service.src.api.schemas.health import HealthSchema

API_URL = "api/v1/auth/"

async def test__healthcheck__status__ok(
        client: AsyncClient,
):
    result = await client.get(
        f"{API_URL}health",
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json() == HealthSchema(is_alive=True).model_dump()

