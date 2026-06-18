from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.broker.consumer import KafkaConsumer
from src.broker.producer import KafkaProducer
from src.config import Settings
from src.services.saga import SagaService


class BrokerProvider(Provider):
    """Dishka provider that wires Kafka producer and consumer."""

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.APP)
    def kafka_produced(self) -> KafkaProducer:
        """Provide a singleton Kafka producer instance."""
        return KafkaProducer(settings=self.__settings)

    @provide(scope=Scope.APP)
    def kafka_consumer(self, session_factory: async_sessionmaker[AsyncSession], saga_service: SagaService) -> KafkaConsumer:
        """Provide a singleton Kafka consumer instance."""
        return KafkaConsumer(
            settings=self.__settings,
            session_factory=session_factory,
            saga_service=saga_service
        )
