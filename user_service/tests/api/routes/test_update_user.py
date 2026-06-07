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
    user_profile_for_update = await create_user_profile_table()
    result = await client.patch(
        f"{API_URL}/{user_profile_for_update.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
        json={
            "roles": [UserRoles.ROLE_ADMIN.value],
        }
    )

    assert result.status_code == HTTPStatus.OK

async def test__delete_user__response__ok(
        client: AsyncClient,
        create_user_profile_table: Callable,
        create_auth_headers: Callable,
):
    roles_for_update = [UserRoles.ROLE_ADMIN.value]
    user_profile_for_auth = await create_user_profile_table(roles=roles_for_update)
    user_profile_for_update = await create_user_profile_table()
    result = await client.patch(
        f"{API_URL}/{user_profile_for_update.user_id}",
        headers=await create_auth_headers(user_profile=user_profile_for_auth),
        json={
            "roles": roles_for_update,
        }
    )
    assert result.json().get("roles") == roles_for_update