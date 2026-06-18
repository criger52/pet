import uuid
from collections.abc import Sequence

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import UserProfileTable
from src.db.user_roles import UserRoles


class UserProfileTableFactory:

    @staticmethod
    async def create(
            roles: Sequence[UserRoles] | None = None,
            user_id: uuid.UUID | None = None,
    ) -> UserProfileTable:
        user_profile = UserProfileTable(
            roles=roles if roles is not None else [],
            user_id=user_id or uuid.uuid4(),
        )
        return user_profile




@pytest.fixture
async def create_user_profile_table(session: AsyncSession):

    async def _create_user_profile(
            roles: Sequence[UserRoles] | None = None,
            user_id: uuid.UUID | None = None,
    ) -> UserProfileTable:
        user = await UserProfileTableFactory.create(
            roles=roles,
            user_id=user_id,
        )
        session.add(user)
        await session.commit()
        return user


    return _create_user_profile
