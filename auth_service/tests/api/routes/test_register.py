from http import HTTPStatus
from typing import Callable
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.api.schemas.user import UserResponse


API_URL = "api/v1/auth/"


async def test__register__status__created(
        client: AsyncClient,
):
    with patch("src.broker.producer.KafkaProducer.send_event", new_callable=AsyncMock):
        result = await client.post(
            f"{API_URL}register",
            json={
                "email": "test@example.com",
                "password": "test_pswd1"
            }
        )
    assert result.status_code == HTTPStatus.CREATED

async def test__register__response__ok(
        client: AsyncClient,
):
    with patch("src.broker.producer.KafkaProducer.send_event", new_callable=AsyncMock):
        result = await client.post(
            f"{API_URL}register",
            json={
                "email": "test@example.com",
                "password": "test_pswd1"
            }
        )

    json = UserResponse.model_validate(result.json())
    assert json.id
    assert "test@example.com" == json.email

async def test__register__status__conflict(
        client: AsyncClient,
        create_user_table: Callable
):
    email = "test@example.com"
    await create_user_table(email=email)
    with patch("src.broker.producer.KafkaProducer.send_event", new_callable=AsyncMock):
        result = await client.post(
            f"{API_URL}register",
            json={
                "email": email,
                "password": "test_pswd1"
            }
        )
    assert result.status_code == HTTPStatus.CONFLICT