import logging

from dishka import FromDishka
from sqlalchemy import delete, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import UserProfileTable
from src.db.user_roles import UserRoles


logger = logging.getLogger(__name__)


class UserProfileService:
    """Manages user profile records in the database."""

    def __init__(self, session: FromDishka[AsyncSession]):
        self.__session = session

    async def create_user_profile(self, user_data) -> None:
        """Create a new user profile from a Kafka user.created event."""
        stmt = (
            insert(UserProfileTable)
            .values(
                user_id=user_data.get("user_id"),
            )
        )

        try:
            await self.__session.execute(stmt)
            await self.__session.commit()
            logger.info(f"User profile created: user_id={user_data.get("user_id")}")
        except Exception as e:
            logger.error("Failed to create profile for user_id=%s: %s", user_data.get("user_id"), e)
            raise e

    async def fetch_user_by_id(self, user_id: str):
        """Fetch a user profile by auth service user ID."""
        stmt = (
            select(UserProfileTable)
            .where(UserProfileTable.user_id == user_id)
        )

        try:
            result = await self.__session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Failed to fetch user_id=%s: %s", user_id, e)
            raise e

    async def fetch_user_list(self):
        """Fetch all user profiles."""
        stmt = select(UserProfileTable)
        try:
            result = await self.__session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to fetch user list: %s", e)
            raise e

    async def delete_user_profile(self, user_id: str):
        """Delete a user profile by auth service user ID."""
        stmt = (
            delete(UserProfileTable)
            .where(UserProfileTable.user_id == user_id)
        )

        try:
            await self.__session.execute(stmt)
            await self.__session.commit()
            logger.info("User profile deleted: user_id=%s", user_id)
        except Exception as e:
            logger.error("Failed to delete user_id=%s: %s", user_id, e)
            raise e

    async def update_user_roles(self, user_id: str, roles: list[UserRoles]):
        """Update roles for an existing user profile."""
        user_profile = await self.fetch_user_by_id(user_id=user_id)

        if not user_profile:
            logger.info("User not found for role update: user_id=%s", user_id)
            return None

        user_profile.roles = [role.value for role in roles]
        await self.__session.commit()
        await self.__session.refresh(user_profile)

        logger.info("Roles updated for user_id=%s: %s", user_id, user_profile.roles)
        return user_profile
