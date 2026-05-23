from dishka import AsyncContainer, FromDishka, Provider, Scope, provide

from src.broker.consumer import KafkaConsumer
from src.config import Settings


class BrokerProvider(Provider):

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.APP)
    def kafka_consumer(self, container: FromDishka[AsyncContainer]) -> KafkaConsumer:
        return KafkaConsumer(settings=self.__settings, container=container)