from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.config import Settings
from src.services.healthcheck import HealthCheckService
from src.services.login import LoginService
from src.services.outbox import OutBoxService
from src.services.register import RegisterService
from src.services.saga import SagaService


class ServicesProvider(Provider):
    """Dishka provider that wires auth service business logic."""

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.REQUEST)
    def healthcheck_service(self, session: AsyncSession) -> HealthCheckService:
        """Provide a request-scoped health check service."""
        return HealthCheckService(session)

    @provide(scope=Scope.REQUEST)
    def login_service(self, session: AsyncSession) -> LoginService:
        """Provide a request-scoped login service."""
        return LoginService(session=session, settings=self.__settings)

    @provide(scope=Scope.REQUEST)
    def outbox_service(self) -> OutBoxService:
        """Provide a request-scoped outbox service."""
        return OutBoxService()

    @provide(scope=Scope.REQUEST)
    def register_service(self, session: AsyncSession, outbox_service: OutBoxService) -> RegisterService:
        """Provide a request-scoped registration service."""
        return RegisterService(
            session=session,
            outbox_service=outbox_service,
        )

    @provide(scope=Scope.APP)
    def saga_service(self, session_factory: async_sessionmaker[AsyncSession]) -> SagaService:
        """Provide a request-scoped saga service."""
        return SagaService(
            session_factory=session_factory
        )
