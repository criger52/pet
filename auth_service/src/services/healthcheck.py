from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import text
from src.db import get_async_session


class HealthCheckService:

    def __init__(self, session: AsyncSession):
        self.__session = session


    async def health_check(self) -> bool:
        try:
            await self.__session.execute(text("SELECT 1"))
        except (TimeoutError, SQLAlchemyError):
            return False
        return True

async def get_healthcheck_service(
    session: AsyncSession = Depends(get_async_session)
) -> HealthCheckService:
    return HealthCheckService(session=session)