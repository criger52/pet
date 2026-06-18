from unittest.mock import AsyncMock, patch

import pytest

from src.broker.producer import KafkaProducer


async def test__user_kafka_producer__start__ok(
        settings,
) -> None:
    with patch("src.broker.producer.AIOKafkaProducer") as mock_producer_class:
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer

        producer = KafkaProducer(settings=settings)
        await producer.start()

        mock_producer_class.assert_called_once_with(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=mock_producer_class.call_args[1]["value_serializer"],
        )
        mock_producer.start.assert_called_once()


async def test__user_kafka_producer__stop__ok(
        settings,
) -> None:
    producer = KafkaProducer(settings=settings)
    producer.producer = AsyncMock()

    await producer.stop()

    producer.producer.stop.assert_called_once()


async def test__user_kafka_producer__send_event__ok(
        settings,
) -> None:
    producer = KafkaProducer(settings=settings)
    producer.producer = AsyncMock()

    await producer.send_event(
        topic="test-topic",
        key="test-key",
        value={"data": "test"},
    )

    producer.producer.send_and_wait.assert_called_once_with(
        "test-topic",
        key=b"test-key",
        value={"data": "test"},
    )


async def test__user_kafka_producer__send_event__exception(
        settings,
) -> None:
    producer = KafkaProducer(settings=settings)
    producer.producer = AsyncMock()
    producer.producer.send_and_wait.side_effect = Exception("Kafka error")

    with pytest.raises(Exception, match="Kafka error"):
        await producer.send_event(
            topic="test-topic",
            key="test-key",
            value={"data": "test"},
        )


async def test__user_kafka_producer__stop__no_producer(
        settings,
) -> None:
    producer = KafkaProducer(settings=settings)
    producer.producer = None

    await producer.stop()
