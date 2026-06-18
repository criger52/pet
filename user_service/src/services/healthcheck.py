import logging

from dishka import FromDishka
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import text


logger = logging.getLogger(__name__)


class HealthCheckService:
    """Checks database connectivity by executing a simple query."""

    def __init__(self, session: FromDishka[AsyncSession]):
        self.__session = session

    async def health_check(self) -> bool:
        """Return True if the database is reachable, False otherwise."""
        try:
            await self.__session.execute(text("SELECT 1"))
        except (TimeoutError, SQLAlchemyError) as e:
            logger.warning(f"Database health check failed: {e}")
            return False
        return True
