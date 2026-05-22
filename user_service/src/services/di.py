from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.services.healthcheck import HealthCheckService


class ServicesProvider(Provider):

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.REQUEST)
    def healthcheck_service(self, session: AsyncSession) -> HealthCheckService:
        return HealthCheckService(session)
