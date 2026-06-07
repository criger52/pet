from http import HTTPStatus
from typing import Callable

from httpx import AsyncClient

from src.api.schemas.user import UserProfileListSchema
from src.db.user_roles import UserRoles


API_URL = "api/v1/user/users"


async def test__fetch_user_list__status__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table(roles=(UserRoles.ROLE_ADMIN.value, ))
    result = await client.get(
        f"{API_URL}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.status_code == HTTPStatus.OK

async def test__fetch_user_list__status__forbidden(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table()
    result = await client.get(
        f"{API_URL}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.status_code == HTTPStatus.FORBIDDEN

async def test__fetch_user_list__status__unauthorized(
        client: AsyncClient,
):
    result = await client.get(
        f"{API_URL}",
        headers={},
    )

    assert result.status_code == HTTPStatus.UNAUTHORIZED
    
async def test__fetch_user_list__response__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table(roles=(UserRoles.ROLE_ADMIN.value, ))
    result = await client.get(
        f"{API_URL}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    response_users = result.json()

    assert len(response_users.get("users")) == 1
    assert response_users == UserProfileListSchema.model_validate(response_users).model_dump(mode="json")
