import uuid

import pytest
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import UserTable
from src.db.user_statuses import UserStatuses
from src.services.register import RegisterService


class UserTableFactory:

    @staticmethod
    async def create(
            email: EmailStr | None = None,
            password: str = "test_pswd1",
            status: UserStatuses = UserStatuses.ACTIVE
    ) -> UserTable:
        user = UserTable(
            email=email or f"{uuid.uuid4()}@example.com",
            password_hash=RegisterService.hash_password(password),
            status=status,
        )
        user.plain_password = password
        return user




@pytest.fixture
async def create_user_table(session: AsyncSession):

    async def _create_user(
            email: EmailStr | None = None,
            status: UserStatuses = UserStatuses.ACTIVE,
            password: str = "tets_pswd1",
    ) -> UserTable:
        if email is None:
            email = f"{uuid.uuid4()}@example.com"
        user = await UserTableFactory.create(email=email, password=password, status=status)
        session.add(user)
        await session.commit()
        return user


    return _create_user
