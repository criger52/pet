from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.db.di import DatabaseProvider
from src.api.routes.router import user_router
from src.config import Settings
from src.services.di import ServicesProvider


class Application:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.container = make_async_container(
            ServicesProvider(settings=self.settings),
            DatabaseProvider(settings=self.settings),
        )

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:

        yield

    def _include_routers(self) -> None:
        self._app.include_router(user_router)

    def create_app(self):
        self._app = FastAPI(
            title=self.settings.SERVICE_NAME,
            version=self.settings.SERVICE_VERSION,
            debug=self.settings.DEBUG,
            lifespan=self.lifespan
        )
        setup_dishka(container=self.container, app=self._app)
        self._include_routers()

        return self._app
