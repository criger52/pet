from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.services.healthcheck import HealthCheckService
from src.services.user_service import UserProfileService


class ServicesProvider(Provider):
    """Dishka provider that wires user service business logic."""

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.REQUEST)
    def healthcheck_service(self, session: AsyncSession) -> HealthCheckService:
        """Provide a request-scoped health check service."""
        return HealthCheckService(session=session)

    @provide(scope=Scope.REQUEST)
    def user_service(self, session: AsyncSession) -> UserProfileService:
        """Provide a request-scoped user profile service."""
        return UserProfileService(session=session)
