import asyncio
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.broker.producer import KafkaProducer
from src.services.outbox import OutBoxService


logger = logging.getLogger(__name__)


class OutBoxWorker:
    """Polls unprocessed outbox events and publishes them to Kafka."""

    def __init__(
            self,
            session_factory: async_sessionmaker,
            outbox_service: OutBoxService,
            kafka_producer: KafkaProducer,
            poll_interval: int = 5,
            batch_size: int = 100,
            max_retries: int = 10,
    ):
        self.session_factory = session_factory
        self.outbox_service = outbox_service
        self.kafka_producer = kafka_producer
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.max_retries = max_retries
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start the worker in background."""
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("Outbox worker started")

    async def stop(self):
        """Stop the worker gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Outbox worker stopped")

    async def _run(self):
        """Main worker loop."""
        while self._running:
            try:
                await self._process_batch()
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
            await asyncio.sleep(self.poll_interval)

    async def _process_batch(self):
        """Fetch and process a batch of unprocessed outbox events."""
        async with self.session_factory() as session:
            events = await self.outbox_service.get_unprocessed_events(
                session, self.batch_size
            )

            if not events:
                return

            logger.info(f"Found {len(events)} events to send")

            for event in events:
                await self._process_event(session, event)

            await session.commit()

    async def _process_event(self, session, event):
        """Publish a single outbox event to Kafka and mark it as processed."""
        try:
            topic = self._get_topic_for_event(event)

            await self.kafka_producer.send_event(
                topic=topic,
                key=str(event.aggregate_id),
                value=event.payload
            )

            await self.outbox_service.mark_as_processed(session, event.id)
            logger.info(f"Event {event.event_id} sent successfully")

        except Exception as e:
            logger.error(f"Failed to send event {event.event_id}: {e}")

            if event.retries >= self.max_retries:
                await self.outbox_service.delete_event(session, event.id)
                logger.warning(
                    f"Event {event.event_id} deleted after {self.max_retries} retries"
                )
            else:
                await self.outbox_service.increment_retries(session, event.id)
                logger.info(
                    f"Event {event.event_id} retry {event.retries + 1}/{self.max_retries}"
                )

    def _get_topic_for_event(self, event) -> str:
        """Determine Kafka topic by event type."""
        match event.event_type:
            case "USER_CREATED":
                return "user.created"
            case "USER_UPDATED":
                return "user.updated"
            case "USER_DELETED":
                return "user.deleted"
            case _:
                raise ValueError(f"Unknown event type: {event.event_type}")