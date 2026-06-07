from http import HTTPStatus
from typing import Callable

from httpx import AsyncClient

from src.db.user_roles import UserRoles


API_URL = "api/v1/user/users"

async def test__delete_user__status__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table(roles=(UserRoles.ROLE_ADMIN.value, ))
    user_profile_for_delete = await create_user_profile_table()
    result = await client.delete(
        f"{API_URL}/{user_profile_for_delete.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.status_code == HTTPStatus.NO_CONTENT


async def test__delete_user__user_really_deleted__not_found(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_auth = await create_user_profile_table(roles=(UserRoles.ROLE_ADMIN.value,))
    user_profile_for_delete = await create_user_profile_table()

    delete_result = await client.delete(
        f"{API_URL}/{user_profile_for_delete.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert delete_result.status_code == HTTPStatus.NO_CONTENT

    update_result = await client.get(
        f"{API_URL}/{user_profile_for_delete.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert update_result.status_code == HTTPStatus.NOT_FOUND

async def test__delete_user__status__unauthorized(
        client: AsyncClient,
        create_user_profile_table: Callable,
):
    user_profile_for_delete = await create_user_profile_table()
    result = await client.delete(
        f"{API_URL}/{user_profile_for_delete.user_id}",
        headers={},
    )

    assert result.status_code == HTTPStatus.UNAUTHORIZED

async def test__delete_user__status__forbidden(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    user_profile_for_delete = await create_user_profile_table(roles=(UserRoles.ROLE_MANAGER.value, ))
    user_profile_for_auth = await create_user_profile_table()
    result = await client.delete(
        f"{API_URL}/{user_profile_for_delete.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
    )

    assert result.status_code == HTTPStatus.FORBIDDEN