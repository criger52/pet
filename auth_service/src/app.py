from fastapi import FastAPI, APIRouter

from src.api.routes.router import auth_router
from src.config import Settings


class Application:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._app: FastAPI

    def _include_routers(self) -> None:
        self._app.include_router(auth_router)

    def create_app(self):
        self._app = FastAPI(
            title=self.settings.AUTH_SERVICE_NAME,
            version=self.settings.AUTH_SERVICE_VERSION,
            debug=self.settings.AUTH_DEBUG,
        )
        self._include_routers()

        return self._app
