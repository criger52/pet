from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.testing.pickleable import User
from sqlalchemy import select


async_engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/postgres')

async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)
