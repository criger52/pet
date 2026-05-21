from http import HTTPStatus
from typing import Callable
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.api.schemas.user import LoginResponse
from src.services.login import LoginService


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


async def test__login__status__wrong_password(
        client: AsyncClient,
        create_user_table: Callable,
):
    user = await create_user_table(email="test@example.com")

    result = await client.post(
        f"{API_URL}login",
        json={
            "email": user.email,
            "password": "wrong_password",
        },
    )

    assert result.status_code == HTTPStatus.UNAUTHORIZED


async def test__login__status__internal_error(
        client: AsyncClient,
):
    with patch.object(
        LoginService,
        "login",
        AsyncMock(side_effect=RuntimeError("unexpected")),
    ):
        result = await client.post(
            f"{API_URL}login",
            json={
                "email": "test@example.com",
                "password": "test_pswd1",
            },
        )

    assert result.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
