import asyncio
import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.broker.producer import KafkaProducer
from src.config import get_settings
from src.services.outbox import OutBoxService
from src.workers.outbox_worker import OutBoxWorker


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    """Управление жизненным циклом worker."""
    settings = get_settings()

    engine = create_async_engine(settings.AUTH_SERVICE_DB_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    kafka = KafkaProducer(settings)
    await kafka.start()

    outbox_service = OutBoxService()
    worker = OutBoxWorker(
        session_factory=session_factory,
        outbox_service=outbox_service,
        kafka_producer=kafka
    )

    await worker.start()

    try:
        yield
    finally:
        await worker.stop()
        await kafka.stop()
        await engine.dispose()


async def main():
    """Entry point."""
    async with lifespan():
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
