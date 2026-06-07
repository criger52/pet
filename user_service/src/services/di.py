from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.services.healthcheck import HealthCheckService
from src.services.user_service import UserProfileService


class ServicesProvider(Provider):

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.REQUEST)
    def healthcheck_service(self, session: AsyncSession) -> HealthCheckService:
        return HealthCheckService(session=session)

    @provide(scope=Scope.REQUEST)
    def user_service(self, session: AsyncSession) -> UserProfileService:
        return UserProfileService(session=session)
