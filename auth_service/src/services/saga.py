import logging
import uuid
from datetime import datetime

from sqlalchemy import update

from src.db.tables import UserTable
from src.db.user_statuses import UserStatuses


logger = logging.getLogger(__name__)


class SagaService:
    """Handles SAGA compensation and completion logic."""

    def __init__(self, session_factory):
        self.__session_factory = session_factory

    async def handle_failed_registration(self, user_id: str, error: str):
        """Handle failed user creation - compensation."""

        stmt = (
            update(UserTable)
            .where(UserTable.id == uuid.UUID(user_id))
            .values(
                status=UserStatuses.FAILED.value,
                error_message=error,
                completed_at=datetime.now()
            )
        )
        async with self.__session_factory() as session:
            try:
                await session.execute(stmt)
                await session.commit()
                logger.warning(f"User {user_id} deleted by saga compensation: {error}")
            except Exception:
                await session.rollback()
                # TODO: обработьт тут надо навырон что то топи rolback итд
                logger.error("Failed to compensate user", exc_info=True)


    async def handle_successful_registration(self, user_id: str):
        """Handle successful user creation."""
        stmt = (
            update(UserTable)
            .where(UserTable.id == uuid.UUID(user_id))
            .values(
                status=UserStatuses.ACTIVE.value,
                completed_at=datetime.now()
            )
        )
        async with self.__session_factory() as session:
            try:
                await session.execute(stmt)
                await session.commit()
                logger.info(f"User {user_id} registration confirmed")
            except Exception:
                # TODO:

                logger.error("Failed to compensate user", exc_info=True)