import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from dishka import AsyncContainer

from src.broker.message_statuses import MessageStatuses
from src.broker.producer import KafkaProducer
from src.config import Settings
from src.services.user_service import UserProfileService


logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Listens for user.created events and creates user profiles."""

    def __init__(self, settings: Settings, container: AsyncContainer, producer: KafkaProducer):
        """Initialize the consumer with settings and a DI container."""
        self.settings = settings
        self.container = container
        self.producer = producer

    async def start(self):
        """Start the Kafka consumer and begin processing messages."""
        logger.info("Starting Kafka consumer on topic user.created")
        self.consumer = AIOKafkaConsumer(
            "user.created",
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="user-service-group",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self.consumer.start()
        self._consume_task = asyncio.create_task(self._consume())

    async def _consume(self):
        """Process incoming user.created messages."""
        try:
            async for msg in self.consumer:
                data = msg.value
                user_id = data.get("user_id")
                logger.info(f"Received reply: user_id={user_id}, status={data.get('status')}")

                async with self.container() as request_container:
                    user_service = await request_container.get(UserProfileService)
                    try:
                        await user_service.create_user_profile(data)
                        await self.producer.send_event(
                            topic="user.created.reply",
                            key=user_id,
                            value={
                                "user_id": user_id,
                                "status": MessageStatuses.SUCCESS.value,
                                "error": None
                            }
                        )
                        logger.info(f"Profile created for user {user_id}")
                    except Exception as e:
                        await self.producer.send_event(
                            topic="user.created.reply",
                            key=user_id,
                            value={
                                "user_id": user_id,
                                "status": MessageStatuses.FAILED.value,
                                "error": str(e)
                            }
                        )
                        logger.error(f"Profile creation error: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)

    async def stop(self):
        """Stop the consumer and cancel the processing task."""
        logger.info("Stopping Kafka consumer")
        if self._consume_task:
            self._consume_task.cancel()
        if self.consumer:
            await self.consumer.stop()
