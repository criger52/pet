from dishka import FromDishka
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import text


class HealthCheckService:

    def __init__(self, session: FromDishka[AsyncSession]):
        self.__session = session


    async def health_check(self) -> bool:
        try:
            await self.__session.execute(text("SELECT 1"))
        except (TimeoutError, SQLAlchemyError):
            return False
        return True
