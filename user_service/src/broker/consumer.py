import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from src.config import Settings
from src.services.user_service import UserService


logger = logging.getLogger(__name__)

class KafkaConsumer:

    def __init__(self, settings: Settings, container):
        self.settings = settings
        self.container = container

    async def start(self):
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
        try:
            async for msg in self.consumer:
                user_data = msg.value
                logger.info(f"Received message: {user_data}")
                async with self.container() as request_container:
                    user_service = await request_container.get(UserService)
                    await user_service.create_user_profile(user_data)
        except Exception as e:
            logger.error(e)

    async def stop(self):
        if self._consume_task:
            self._consume_task.cancel()
        if self.consumer:
            await self.consumer.stop()
