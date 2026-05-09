import pytest
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)


@pytest.fixture
async def async_engine():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        echo=False
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session_maker(async_engine):
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return async_session_maker


@pytest.fixture
async def session(async_session_maker):
    async with async_session_maker() as session:
        yield session
        await session.rollback()
