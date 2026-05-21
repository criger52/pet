from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.broker.producer import KafkaProducer
from src.config import Settings
from src.services.healthcheck import HealthCheckService
from src.services.login import LoginService
from src.services.register import RegisterService


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

    @provide(scope=Scope.REQUEST)
    def login_service(self, session: AsyncSession) -> LoginService:
        return LoginService(session=session, settings=self.__settings)

    @provide(scope=Scope.REQUEST)
    def register_service(self, session: AsyncSession, kafka_producer: KafkaProducer) -> RegisterService:
        return RegisterService(
            session=session,
            kafka_producer=kafka_producer,
        )
