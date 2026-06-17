from unittest.mock import AsyncMock, MagicMock, patch

from src.broker.consumer import KafkaConsumer


async def test__kafka_consumer__start__ok(
        settings,
        async_session_maker,
        saga_service,
) -> None:
    with patch("src.broker.consumer.AIOKafkaConsumer") as mock_consumer_class:
        mock_consumer = AsyncMock()
        mock_consumer_class.return_value = mock_consumer

        consumer = KafkaConsumer(
            settings=settings,
            session_factory=async_session_maker,
            saga_service=saga_service,
        )

        await consumer.start()

        mock_consumer_class.assert_called_once_with(
            "user.created.reply",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="auth-saga-group",
            auto_offset_reset="earliest",
            value_deserializer=mock_consumer_class.call_args[1]["value_deserializer"],
        )
        mock_consumer.start.assert_called_once()
        assert consumer._task is not None


async def test__kafka_consumer__listen__failed_status(
        settings,
        async_session_maker,
        saga_service,
) -> None:
    consumer = KafkaConsumer(
        settings=settings,
        session_factory=async_session_maker,
        saga_service=saga_service,
    )
    consumer.consumer = AsyncMock()

    mock_message = MagicMock()
    mock_message.value = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "failed",
        "error": "Profile creation failed",
    }

    with patch.object(consumer, "_listen") as mock_listen:
        await consumer._listen()

        mock_listen.assert_called_once()


async def test__kafka_consumer__listen__success_status(
        settings,
        async_session_maker,
        saga_service,
) -> None:
    consumer = KafkaConsumer(
        settings=settings,
        session_factory=async_session_maker,
        saga_service=saga_service,
    )

    mock_message = MagicMock()
    mock_message.value = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "success",
    }

    with patch.object(consumer, "_listen") as mock_listen:
        await consumer._listen()

        mock_listen.assert_called_once()
