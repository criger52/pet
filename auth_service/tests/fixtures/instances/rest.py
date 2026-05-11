from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.app import Application
from src.config import get_settings


@pytest.fixture
def app() -> FastAPI:
    settings = get_settings()
    app = Application(settings).create_app()
    return app


@pytest.fixture
async def client(app: FastAPI, async_engine) -> AsyncIterator[AsyncClient]: # , engine
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
