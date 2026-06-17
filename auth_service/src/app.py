import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.api.routes.router import auth_router
from src.broker.consumer import KafkaConsumer
from src.broker.di import BrokerProvider
from src.broker.producer import KafkaProducer
from src.config import Settings
from src.db.di import DatabaseProvider
from src.services.di import ServicesProvider


logger = logging.getLogger(__name__)


class Application:
    """Builds and configures the auth service FastAPI application."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the application with settings and DI container."""
        self.settings = settings
        self.container = make_async_container(
            DatabaseProvider(settings=self.settings),
            ServicesProvider(settings=self.settings),
            BrokerProvider(settings=self.settings),
        )

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        """Manage Kafka producer lifecycle on app startup and shutdown."""
        kafka_producer = await self.container.get(KafkaProducer)
        kafka_consumer = await self.container.get(KafkaConsumer)

        logger.info("Starting Kafka producer")
        await kafka_producer.start()

        logger.info("Starting Kafka consumer")
        await kafka_consumer.start()

        yield

        logger.info("Stopping Kafka producer")
        await kafka_producer.stop()
        logger.info("Stopping Kafka consumer")
        await kafka_consumer.stop()

    def _include_routers(self) -> None:
        """Mount all API routers on the FastAPI application."""
        self._app.include_router(auth_router)

    def create_app(self) -> FastAPI:
        """Create and return a fully configured FastAPI application."""
        self._app = FastAPI(
            title=self.settings.SERVICE_NAME,
            version=self.settings.SERVICE_VERSION,
            debug=self.settings.DEBUG,
            lifespan=self._lifespan,
        )
        setup_dishka(container=self.container, app=self._app)
        self._include_routers()
        logger.info(f"Application created: {self.settings.SERVICE_NAME} on {self.settings.SERVICE_VERSION}")

        return self._app
