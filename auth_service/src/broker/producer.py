import json

from aiokafka import AIOKafkaProducer

from src.config import Settings


class KafkaProducer:

    def __init__(self, settings: Settings):
        self.settings = settings

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()

    async def send_event(self, topic: str, key: str, value: dict):
        await self.producer.send(topic, key=key.encode(), value=value)
        await self.producer.flush()

    async def stop(self):
        if self.producer:
            await self.producer.stop()
