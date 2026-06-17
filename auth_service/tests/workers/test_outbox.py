import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.workers.outbox_worker import OutBoxWorker


async def test__outbox_worker__start__ok(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
            poll_interval=1,
            batch_size=10,
            max_retries=3,
        )

        await worker.start()

        assert worker._running is True
        assert worker._task is not None


async def test__outbox_worker__stop__ok(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        worker._running = True

        async def dummy_task():
            try:
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                pass

        worker._task = asyncio.create_task(dummy_task())

        await worker.stop()

        assert worker._running is False
        assert worker._task.cancelled() is True


async def test__outbox_worker__process_batch__no_events(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        outbox_service.get_unprocessed_events = AsyncMock(return_value=[])

        with patch("src.workers.outbox_worker.async_sessionmaker") as mock_sessionmaker:
            mock_session = AsyncMock()
            mock_sessionmaker.return_value.__aenter__.return_value = mock_session

            await worker._process_batch()

            outbox_service.get_unprocessed_events.assert_called_once()
            mock_kafka.send_event.assert_not_called()


async def test__outbox_worker__process_batch__with_events(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        mock_session = AsyncMock()
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.event_id = uuid.uuid4()
        mock_event.aggregate_id = uuid.uuid4()
        mock_event.event_type = "USER_CREATED"
        mock_event.payload = {"user_id": str(uuid.uuid4())}
        mock_event.retries = 0

        mock_mark = AsyncMock()
        outbox_service.mark_as_processed = mock_mark

        await worker._process_event(mock_session, mock_event)

        mock_kafka.send_event.assert_called_once_with(
            topic="user.created",
            key=str(mock_event.aggregate_id),
            value=mock_event.payload,
        )
        mock_mark.assert_called_once_with(mock_session, mock_event.id)


async def test__outbox_worker__process_event__success(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        mock_session = AsyncMock()
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.event_id = uuid.uuid4()
        mock_event.aggregate_id = uuid.uuid4()
        mock_event.event_type = "USER_CREATED"
        mock_event.payload = {"user_id": str(uuid.uuid4())}
        mock_event.retries = 0

        outbox_service.mark_as_processed = AsyncMock()

        await worker._process_event(mock_session, mock_event)

        mock_kafka.send_event.assert_called_once_with(
            topic="user.created",
            key=str(mock_event.aggregate_id),
            value=mock_event.payload,
        )
        outbox_service.mark_as_processed.assert_called_once_with(
            mock_session,
            mock_event.id,
        )


async def test__outbox_worker__process_event__retry(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
            max_retries=3,
        )

        mock_session = AsyncMock()
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.event_id = uuid.uuid4()
        mock_event.aggregate_id = uuid.uuid4()
        mock_event.event_type = "USER_CREATED"
        mock_event.payload = {"user_id": str(uuid.uuid4())}
        mock_event.retries = 1

        mock_kafka.send_event.side_effect = Exception("Kafka error")

        mock_increment = AsyncMock()
        mock_mark = AsyncMock()
        outbox_service.increment_retries = mock_increment
        outbox_service.mark_as_processed = mock_mark

        await worker._process_event(mock_session, mock_event)

        mock_increment.assert_called_once_with(mock_session, mock_event.id)
        mock_mark.assert_not_called()


async def test__outbox_worker__process_event__max_retries_exceeded(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
            max_retries=3,
        )

        mock_session = AsyncMock()
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.event_id = uuid.uuid4()
        mock_event.aggregate_id = uuid.uuid4()
        mock_event.event_type = "USER_CREATED"
        mock_event.payload = {"user_id": str(uuid.uuid4())}
        mock_event.retries = 3

        mock_kafka.send_event.side_effect = Exception("Kafka error")

        mock_delete = AsyncMock()
        mock_increment = AsyncMock()
        outbox_service.delete_event = mock_delete
        outbox_service.increment_retries = mock_increment

        await worker._process_event(mock_session, mock_event)

        mock_delete.assert_called_once_with(mock_session, mock_event.id)
        mock_increment.assert_not_called()


async def test__outbox_worker__get_topic_for_event__user_created(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        mock_event = MagicMock()
        mock_event.event_type = "USER_CREATED"

        topic = worker._get_topic_for_event(mock_event)
        assert topic == "user.created"


async def test__outbox_worker__get_topic_for_event__user_updated(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        mock_event = MagicMock()
        mock_event.event_type = "USER_UPDATED"

        topic = worker._get_topic_for_event(mock_event)
        assert topic == "user.updated"


async def test__outbox_worker__get_topic_for_event__user_deleted(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        mock_event = MagicMock()
        mock_event.event_type = "USER_DELETED"

        topic = worker._get_topic_for_event(mock_event)
        assert topic == "user.deleted"


async def test__outbox_worker__get_topic_for_event__unknown(
        async_session_maker,
        outbox_service,
) -> None:
    with patch("src.workers.outbox_worker.KafkaProducer") as mock_producer_class:
        mock_kafka = AsyncMock()
        mock_producer_class.return_value = mock_kafka

        worker = OutBoxWorker(
            session_factory=async_session_maker,
            outbox_service=outbox_service,
            kafka_producer=mock_kafka,
        )

        mock_event = MagicMock()
        mock_event.event_type = "UNKNOWN_EVENT"

        with pytest.raises(ValueError, match="Unknown event type: UNKNOWN_EVENT"):
            worker._get_topic_for_event(mock_event)
