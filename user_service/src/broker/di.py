from dishka import AsyncContainer, FromDishka, Provider, Scope, provide

from src.broker.consumer import KafkaConsumer
from src.broker.producer import KafkaProducer
from src.config import Settings


class BrokerProvider(Provider):
    """Dishka provider."""

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.APP)
    def kafka_producer(self) -> KafkaProducer:
        """Provide a singleton Kafka producer instance."""
        return KafkaProducer(settings=self.__settings)

    @provide(scope=Scope.APP)
    def kafka_consumer(self, container: FromDishka[AsyncContainer], producer: FromDishka[KafkaProducer]) -> KafkaConsumer:
        """Provide a singleton Kafka consumer instance."""
        return KafkaConsumer(settings=self.__settings, container=container, producer=producer)
