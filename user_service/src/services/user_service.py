import logging

from dishka import FromDishka
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import UserProfileTable


logger = logging.getLogger(__name__)

class UserService:

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
