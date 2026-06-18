from unittest.mock import AsyncMock, MagicMock, patch

from src.broker.consumer import KafkaConsumer


async def test__user_kafka_consumer__start__ok(
        settings,
) -> None:
    with patch("src.broker.consumer.AIOKafkaConsumer") as mock_consumer_class:
        mock_consumer = AsyncMock()
        mock_consumer_class.return_value = mock_consumer

        with patch("src.broker.consumer.AsyncContainer") as mock_container_class:
            mock_container = AsyncMock()
            mock_container_class.return_value = mock_container

            with patch("src.broker.consumer.KafkaProducer") as mock_producer_class:
                mock_producer = AsyncMock()
                mock_producer_class.return_value = mock_producer

                consumer = KafkaConsumer(
                    settings=settings,
                    container=mock_container,
                    producer=mock_producer,
                )

                await consumer.start()

                mock_consumer_class.assert_called_once_with(
                    "user.created",
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id="user-service-group",
                    auto_offset_reset="earliest",
                    value_deserializer=mock_consumer_class.call_args[1]["value_deserializer"],
                )
                mock_consumer.start.assert_called_once()
                assert consumer._consume_task is not None


async def test__user_kafka_consumer__stop__ok(
        settings,
) -> None:
    with patch("src.broker.consumer.AsyncContainer") as mock_container_class:
        mock_container = AsyncMock()
        mock_container_class.return_value = mock_container

        with patch("src.broker.consumer.KafkaProducer") as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer

            consumer = KafkaConsumer(
                settings=settings,
                container=mock_container,
                producer=mock_producer,
            )

            consumer.consumer = AsyncMock()
            mock_task = MagicMock()
            mock_task.cancel = MagicMock(return_value=None)
            consumer._consume_task = mock_task

            await consumer.stop()

            mock_task.cancel.assert_called_once()
            consumer.consumer.stop.assert_called_once()





async def test__user_kafka_consumer__consume__consumer_error(
        settings,
) -> None:
    with patch("src.broker.consumer.AsyncContainer") as mock_container_class:
        mock_container = AsyncMock()
        mock_container_class.return_value = mock_container

        with patch("src.broker.consumer.KafkaProducer") as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer

            consumer = KafkaConsumer(
                settings=settings,
                container=mock_container,
                producer=mock_producer,
            )
            mock_consumer = AsyncMock()
            mock_consumer.__aiter__ = MagicMock(return_value=MagicMock())
            mock_consumer.__aiter__.return_value.__anext__ = AsyncMock(
                side_effect=Exception("Consumer error")
            )
            consumer.consumer = mock_consumer

            await consumer._consume()
