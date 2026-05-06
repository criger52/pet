from http import HTTPStatus

import pytest
from httpx import AsyncClient

from auth_service.src.api.schemas.health import HealthSchema


@pytest.mark.asyncio
async def test__healthcheck__status__ok():
    async with AsyncClient() as client:
        result = await client.get(
            "http://localhost:8000/api/v1/auth/health",
        )

    assert result.status_code == HTTPStatus.OK
    assert result.json() == HealthSchema(is_alive=True).model_dump()

