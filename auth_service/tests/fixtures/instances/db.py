import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.tables import Base


@pytest.fixture(scope="session")
async def setup_database() -> str:
    db_name = "auth_test"
    dsn = "postgresql+asyncpg://auth:auth@127.0.0.1:5432/postgres"
    admin_engine = create_async_engine(dsn, isolation_level="AUTOCOMMIT")

    async with admin_engine.begin() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        await conn.execute(text(f"CREATE DATABASE {db_name}"))

    await admin_engine.dispose()
    return db_name

@pytest.fixture
async def async_engine(
        setup_database,
        settings
):

    async_engine = create_async_engine(settings.DB_URL, echo=False)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine


    await async_engine.dispose()


@pytest.fixture
async def async_session_maker(async_engine):
    return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(async_session_maker):
    async with async_session_maker() as session:
        yield session

@pytest.fixture(autouse=True)
async def cleanup(async_engine):
    yield
    async with async_engine.begin() as conn:
        tables = Base.metadata.tables.keys()
        for table in tables:
            await conn.execute(text(f"TRUNCATE {table} CASCADE"))