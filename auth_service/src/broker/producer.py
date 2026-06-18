import json
import logging

from aiokafka import AIOKafkaProducer

from src.config import Settings


logger = logging.getLogger(__name__)


class KafkaProducer:
    """Async Kafka producer for publishing domain events."""

    def __init__(self, settings: Settings):
        """Initialize the producer with Kafka connection settings."""
        self.settings = settings

    async def start(self):
        """Connect to Kafka and start the producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()
        logger.info("Producer started")

    async def send_event(self, topic: str, key: str, value: dict):
        """Publish an event to the given Kafka topic."""
        logger.info(f"Sending event to topic={topic} key={key}")
        try:
            await self.producer.send_and_wait(topic, key=key.encode(), value=value)
            logger.info(f"Event sent to topic={topic} key={key}")
        except Exception as e:
            logger.error(f"Kafka send failed for topic={topic} key={key}: {e}")
            raise

    async def stop(self):
        """Disconnect from Kafka and stop the producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Producer stopped")
