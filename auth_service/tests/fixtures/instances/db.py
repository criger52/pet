import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.tables import Base


@pytest.fixture
async def async_engine(
        settings
):

    async_engine = create_async_engine(settings.AUTH_SERVICE_DB_URL, echo=False)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


    await async_engine.dispose()


@pytest.fixture
async def async_session_maker(async_engine):
    return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(async_session_maker):
    async with async_session_maker() as session:
        yield session
