from dishka import Provider, Scope, provide

from src.broker.producer import KafkaProducer
from src.config import Settings


class BrokerProvider(Provider):

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.APP)
    def kafka_produced(self) -> KafkaProducer:
        return KafkaProducer(settings=self.__settings)