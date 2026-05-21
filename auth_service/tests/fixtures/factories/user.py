import uuid
from typing import Optional

import pytest
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import UserTable
from src.services.register import RegisterService


class UserTableFactory:

    @staticmethod
    async def create(
            email: Optional[EmailStr] = None,
            password: str = "test_pswd1",
    ) -> UserTable:
        user = UserTable(
            email=email or f"{uuid.uuid4()}@example.com",
            password_hash=RegisterService.hash_password(password),
        )
        user.plain_password = password
        return user




@pytest.fixture
async def create_user_table(session: AsyncSession):

    async def _create_user(
            email: Optional[EmailStr]  = None,
            password: str = "tets_pswd1",
    ) -> UserTable:
        user = await UserTableFactory.create(email=email, password=password)
        session.add(user)
        await session.commit()
        return user


    return _create_user