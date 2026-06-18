import logging
from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import Settings


logger = logging.getLogger(__name__)


class DatabaseProvider(Provider):
    """Dishka provider that wires the async SQLAlchemy engine and sessions."""

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncGenerator[AsyncEngine, None]:
        """Create and dispose the async database engine."""
        logger.info("Creating database engine")
        engine = create_async_engine(
            pool_pre_ping=True,
            url=self.__settings.USER_SERVICE_DB_URL,
            echo=self.__settings.DEBUG,
        )
        yield engine
        logger.info("Disposing database engine")
        await engine.dispose()

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """Provide a session factory bound to the database engine."""
        return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @provide(scope=Scope.REQUEST)
    async def session(self, session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
        """Provide a request-scoped database session."""
        async with session_factory() as session:
            yield session
