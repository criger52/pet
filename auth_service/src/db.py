import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

DATABASE_URL = os.getenv(
    "AUTH_DB_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
)

async_engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
    finally:
        await session.close()