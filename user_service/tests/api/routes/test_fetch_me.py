from http import HTTPStatus
from typing import Callable

from httpx import AsyncClient

from src.api.schemas.user import UserProfileSchema


API_URL = "api/v1/user/users"


async def test__me__status__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile = await create_user_profile_table()
    result = await client.get(
        f"{API_URL}/me",
        headers=await create_auth_headers(user_profile=user_profile)
    )

    assert result.status_code == HTTPStatus.OK

async def test__me__status__unauthorized(
        client: AsyncClient,
):
    result = await client.get(
        f"{API_URL}/me",
        headers={}
    )

    assert result.status_code == HTTPStatus.UNAUTHORIZED


async def test__me__response__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile = await create_user_profile_table()
    result = await client.get(
        f"{API_URL}/me",
        headers=await create_auth_headers(user_profile=user_profile)
    )
    assert result.json() == UserProfileSchema.model_validate(user_profile).model_dump(mode="json")


