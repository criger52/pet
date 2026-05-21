from http import HTTPStatus
from typing import Callable

from httpx import AsyncClient

from src.api.schemas.user import LoginResponse


API_URL = "api/v1/auth/"


async def test__login__status__ok(
        client: AsyncClient,
        create_user_table: Callable
):
    user = await create_user_table(email="test@example.com")

    result = await client.post(
        f"{API_URL}login",
        json={
            "email": user.email,
            "password": user.plain_password
        }
    )

    assert result.status_code == HTTPStatus.OK


async def test__login__response__ok(
        client: AsyncClient,
        create_user_table: Callable,
):
    user = await create_user_table(email="test@example.com")

    result = await client.post(
        f"{API_URL}login",
        json={
            "email": user.email,
            "password": user.plain_password
        }
    )
    tokens = LoginResponse.model_validate(result.json())
    assert tokens.access_token
    assert tokens.refresh_token


async def test__login__status__unauthorized(
        client: AsyncClient,
):
    result = await client.post(
        f"{API_URL}login",
        json={
            "email": "unknown@example.com",
            "password": "wrong_password",
        },
    )

    assert result.status_code == HTTPStatus.UNAUTHORIZED
