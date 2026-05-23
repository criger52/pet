import json
import logging

from aiokafka import AIOKafkaProducer

from src.config import Settings


logger = logging.getLogger(__name__)

class KafkaProducer:

    def __init__(self, settings: Settings):
        self.settings = settings

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()
        logger.info("Producer started")

    async def send_event(self, topic: str, key: str, value: dict):
        logger.info(f"Sending event to topic: {topic}, key: {key}, value: {value}")
        await self.producer.send(topic, key=key.encode(), value=value)
        await self.producer.flush()
        logger.info(f"Event sent to topic: {topic}, key: {key}, value: {value}")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Producer stopped")
