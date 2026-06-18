import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from src.api.di import AuthProvider
from src.api.routes.router import user_router
from src.broker.consumer import KafkaConsumer
from src.broker.di import BrokerProvider
from src.broker.producer import KafkaProducer
from src.config import Settings
from src.db.di import DatabaseProvider
from src.services.di import ServicesProvider


logger = logging.getLogger(__name__)


class Application:
    """Builds and configures the user service FastAPI application."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the application with settings and DI container."""
        self.settings = settings
        self.container = make_async_container(
            FastapiProvider(),
            ServicesProvider(settings=self.settings),
            DatabaseProvider(settings=self.settings),
            BrokerProvider(settings=self.settings),
            AuthProvider(settings=self.settings),
        )

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        """Manage Kafka lifecycle on app startup and shutdown."""
        kafka_consumer = await self.container.get(KafkaConsumer)
        kafka_producer = await self.container.get(KafkaProducer)
        logger.info("Starting Kafka consumer")
        await kafka_consumer.start()
        logger.info("Starting Kafka producer")
        await kafka_producer.start()

        yield

        logger.info("Stopping Kafka consumer")
        await kafka_consumer.stop()
        logger.info("Stopping Kafka producer")
        await kafka_producer.stop()


    def _include_routers(self) -> None:
        """Mount all API routers on the FastAPI application."""
        self._app.include_router(user_router)

    def create_app(self):
        """Create and return a fully configured FastAPI application."""
        self._app = FastAPI(
            title=self.settings.SERVICE_NAME,
            version=self.settings.SERVICE_VERSION,
            debug=self.settings.DEBUG,
            lifespan=self._lifespan
        )
        setup_dishka(container=self.container, app=self._app)
        self._include_routers()
        logger.info(f"Application created: {self.settings.SERVICE_NAME} on {self.settings.SERVICE_VERSION}")

        return self._app
