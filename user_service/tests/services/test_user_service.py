import uuid
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.db.user_roles import UserRoles
from src.services.user_service import UserProfileService


async def test__user_service__create_user_profile__ok(
        user_service: UserProfileService,
) -> None:
    user_data = {
        "user_id": str(uuid.uuid4()),
        "email": "test@example.com",
    }

    await user_service.create_user_profile(user_data)

    user_profile = await user_service.fetch_user_by_id(user_data["user_id"])
    assert user_profile is not None
    assert str(user_profile.user_id) == user_data["user_id"]


async def test__user_service__create_user_profile__exception(
        user_service: UserProfileService,
) -> None:
    user_data = {
        "user_id": "invalid-uuid",
        "email": "test@example.com",
    }

    with pytest.raises(Exception):
        await user_service.create_user_profile(user_data)


async def test__user_service__fetch_user_by_id__ok(
        user_service: UserProfileService,
        create_user_profile_table,
) -> None:
    user_profile = await create_user_profile_table()

    result = await user_service.fetch_user_by_id(str(user_profile.user_id))

    assert result is not None
    assert result.id == user_profile.id
    assert result.user_id == user_profile.user_id


async def test__user_service__fetch_user_by_id__not_found(
        user_service: UserProfileService,
) -> None:
    result = await user_service.fetch_user_by_id(str(uuid.uuid4()))
    assert result is None


async def test__user_service__fetch_user_by_id__exception(
        user_service: UserProfileService,
) -> None:
    with patch.object(
        user_service._UserProfileService__session,
        "execute",
        side_effect=SQLAlchemyError("DB error"),
    ):
        with pytest.raises(SQLAlchemyError):
            await user_service.fetch_user_by_id(str(uuid.uuid4()))


async def test__user_service__fetch_user_list__ok(
        user_service: UserProfileService,
        create_user_profile_table,
) -> None:
    await create_user_profile_table()
    await create_user_profile_table()

    result = await user_service.fetch_user_list()

    assert len(result) >= 2


async def test__user_service__fetch_user_list__exception(
        user_service: UserProfileService,
) -> None:
    with patch.object(
        user_service._UserProfileService__session,
        "execute",
        side_effect=SQLAlchemyError("DB error"),
    ):
        with pytest.raises(SQLAlchemyError):
            await user_service.fetch_user_list()


async def test__user_service__delete_user_profile__ok(
        user_service: UserProfileService,
        create_user_profile_table,
) -> None:
    user_profile = await create_user_profile_table()

    await user_service.delete_user_profile(str(user_profile.user_id))

    result = await user_service.fetch_user_by_id(str(user_profile.user_id))
    assert result is None


async def test__user_service__delete_user_profile__exception(
        user_service: UserProfileService,
) -> None:
    with patch.object(
        user_service._UserProfileService__session,
        "execute",
        side_effect=SQLAlchemyError("DB error"),
    ):
        with pytest.raises(SQLAlchemyError):
            await user_service.delete_user_profile(str(uuid.uuid4()))


async def test__user_service__update_user_roles__ok(
        user_service: UserProfileService,
        create_user_profile_table,
) -> None:
    user_profile = await create_user_profile_table(roles=[UserRoles.ROLE_USER.value])

    updated = await user_service.update_user_roles(
        user_id=str(user_profile.user_id),
        roles=[UserRoles.ROLE_ADMIN, UserRoles.ROLE_MANAGER],
    )

    assert updated is not None
    assert UserRoles.ROLE_ADMIN.value in updated.roles
    assert UserRoles.ROLE_MANAGER.value in updated.roles


async def test__user_service__update_user_roles__user_not_found(
        user_service: UserProfileService,
) -> None:
    result = await user_service.update_user_roles(
        user_id=str(uuid.uuid4()),
        roles=[UserRoles.ROLE_ADMIN],
    )

    assert result is None


async def test__user_service__update_user_roles__exception(
        user_service: UserProfileService,
        create_user_profile_table,
) -> None:
    user_profile = await create_user_profile_table()

    with patch.object(
        user_service._UserProfileService__session,
        "execute",
        side_effect=SQLAlchemyError("DB error"),
    ):
        with pytest.raises(SQLAlchemyError):
            await user_service.update_user_roles(
                user_id=str(user_profile.user_id),
                roles=[UserRoles.ROLE_ADMIN],
            )
