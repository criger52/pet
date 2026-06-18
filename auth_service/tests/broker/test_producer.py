from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.broker.producer import KafkaProducer
from src.config import Settings


@pytest.fixture
def mock_settings():
    settings = MagicMock(spec=Settings)
    settings.KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
    return settings


async def test__kafka_producer__start__ok(
        mock_settings,
) -> None:
    with patch("src.broker.producer.AIOKafkaProducer") as mock_producer_class:
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer

        producer = KafkaProducer(settings=mock_settings)
        await producer.start()

        mock_producer_class.assert_called_once_with(
            bootstrap_servers="localhost:9092",
            value_serializer=mock_producer_class.call_args[1]["value_serializer"],
        )
        mock_producer.start.assert_called_once()


async def test__kafka_producer__stop__ok(
        mock_settings,
) -> None:
    producer = KafkaProducer(settings=mock_settings)
    producer.producer = AsyncMock()

    await producer.stop()

    producer.producer.stop.assert_called_once()


async def test__kafka_producer__send_event__ok(
        mock_settings,
) -> None:
    producer = KafkaProducer(settings=mock_settings)
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


async def test__kafka_producer__send_event__exception(
        mock_settings,
) -> None:
    producer = KafkaProducer(settings=mock_settings)
    producer.producer = AsyncMock()
    producer.producer.send_and_wait.side_effect = Exception("Kafka error")

    with pytest.raises(Exception, match="Kafka error"):
        await producer.send_event(
            topic="test-topic",
            key="test-key",
            value={"data": "test"},
        )


async def test__kafka_producer__stop__no_producer(
        mock_settings,
) -> None:
    producer = KafkaProducer(settings=mock_settings)
    producer.producer = None

    await producer.stop()
