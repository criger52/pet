import uuid
from http import HTTPStatus
from typing import Callable

from httpx import AsyncClient

from src.api.schemas.user import UserProfileSchema
from src.db.user_roles import UserRoles


API_URL = "api/v1/user/users/"


async def test__fetch_user_by_id__status__forbidden(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table()
    user_profile_for_fetch = await create_user_profile_table()
    result = await client.get(
        f"{API_URL}{user_profile_for_fetch.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.status_code == HTTPStatus.FORBIDDEN

async def test__fetch_user_by_id__status__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table(roles=(UserRoles.ROLE_ADMIN.value, ))
    user_profile_for_fetch = await create_user_profile_table()
    result = await client.get(
        f"{API_URL}{user_profile_for_fetch.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.status_code == HTTPStatus.OK


async def test__fetch_user_by_id__status__not_found(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table(roles=(UserRoles.ROLE_ADMIN.value, ))
    result = await client.get(
        f"{API_URL}{uuid.uuid4()}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.status_code == HTTPStatus.NOT_FOUND

async def test__fetch_user_by_id__response__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table(roles=(UserRoles.ROLE_ADMIN.value, ))
    user_profile_for_fetch = await create_user_profile_table()
    result = await client.get(
        f"{API_URL}{user_profile_for_fetch.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.json() == UserProfileSchema.model_validate(user_profile_for_fetch).model_dump(mode="json")

async def test__fetch_user_by_id__response__forbidden(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table()
    user_profile_for_fetch = await create_user_profile_table()
    result = await client.get(
        f"{API_URL}{user_profile_for_fetch.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.json().get("detail") == "No permissions"
