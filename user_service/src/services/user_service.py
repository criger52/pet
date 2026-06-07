import logging

from dishka import FromDishka
from sqlalchemy import delete, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import UserProfileTable
from src.db.user_roles import UserRoles


logger = logging.getLogger(__name__)

class UserProfileService:

    def __init__(self, session: FromDishka[AsyncSession]):
        self.__session = session

    async def create_user_profile(self, user_data) -> None:
        stmt = (
            insert(UserProfileTable)
            .values(
                user_id=user_data.get("user_id"),
            )
        )

        try:
            await self.__session.execute(stmt)
            await self.__session.commit()
            logger.info(f"User {user_data.get("user_id")}  profile created successfully")
        except Exception as e:
            logger.error(e)
            raise e

    async def fetch_user_by_id(self, user_id: str):
        stmt = (
            select(UserProfileTable)
            .where(UserProfileTable.user_id == user_id)
        )

        try:
            result = await self.__session.execute(stmt)
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(e)
            raise e

    async def fetch_user_list(self):
        stmt = (
            select(UserProfileTable)
        )
        try:
            result = await self.__session.execute(stmt)
            user_list = result.scalars().all()
            return user_list
        except Exception as e:
            logger.error(e)
            raise e

    async def delete_user_profile(self, user_id: str):
        stmt = (
            delete(
                UserProfileTable
            ).where(UserProfileTable.user_id == user_id)
        )

        try:
            await self.__session.execute(stmt)
            await self.__session.commit()
            logger.info(f"User {user_id}  profile deleted successfully")
        except Exception as e:
            logger.error(e)
            raise e

    async def update_user_roles(self, user_id: str, roles: list[UserRoles]):

        user_profile = await self.fetch_user_by_id(user_id=user_id)

        if not user_profile:
            return None

        user_profile.roles = [role.value for role in roles]
        await self.__session.commit()
        await self.__session.refresh(user_profile)

        return user_profile
