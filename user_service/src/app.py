from fastapi import FastAPI

from src.api.routes.router import user_router
from src.config import Settings


class Application:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._app: FastAPI

    def _include_routers(self) -> None:
        self._app.include_router(user_router)

    def create_app(self):
        self._app = FastAPI(
            title=self.settings.SERVICE_NAME,
            version=self.settings.SERVICE_VERSION,
            debug=self.settings.DEBUG,
        )
        self._include_routers()

        return self._app
