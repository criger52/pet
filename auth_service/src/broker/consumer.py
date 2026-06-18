import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from src.broker.message_statuses import MessageStatuses
from src.config import Settings


logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Listens for user.created.reply events and rolls back failed registrations."""

    def __init__(self, settings: Settings, session_factory, saga_service):
        """Initialize the consumer with settings and a database session factory."""
        self.settings = settings
        self.session_factory = session_factory
        self.saga_service = saga_service
        self.consumer = None
        self._task = None

    async def start(self):
        """Start the Kafka consumer and begin listening for messages."""
        logger.info("Starting Kafka consumer on topic user.created.reply")
        self.consumer = AIOKafkaConsumer(
            "user.created.reply",
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="auth-saga-group",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self.consumer.start()
        self._task = asyncio.create_task(self._listen())

    async def _listen(self):
        """Process incoming saga reply messages."""
        async for msg in self.consumer:
            data = msg.value
            user_id, status = data.get("user_id"), data.get("status")

            logger.info(f"Received reply: user_id={user_id}, status={status}")
            try:
                if status == MessageStatuses.FAILED.value:
                    await self.saga_service.handle_failed_registration(
                        user_id=user_id,
                        error=data.get("error")
                    )
                elif status == MessageStatuses.SUCCESS.value:
                    await self.saga_service.handle_successful_registration(
                        user_id=user_id
                    )
            except Exception as e:
                logger.error(f"Failed to process message: {e}")

    async def stop(self):
        """Stop the consumer and cancel the listening task."""
        logger.info("Stopping Kafka consumer")
        if self._task:
            self._task.cancel()
        if self.consumer:
            await self.consumer.stop()
