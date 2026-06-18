from http import HTTPStatus
from typing import Callable
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from src.api.schemas.user import RegistrationResponse
from src.db.user_statuses import UserStatuses
from src.services.register import RegisterService


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
    assert result.status_code == HTTPStatus.ACCEPTED

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

    json = RegistrationResponse.model_validate(result.json())
    assert json.user_id
    assert json.status == UserStatuses.PENDING.value

async def test__register__status__conflict(
        client: AsyncClient,
        create_user_table: Callable
):
    email = "test@example.com"
    await create_user_table(email=email)
    result = await client.post(
        f"{API_URL}register",
        json={
            "email": email,
            "password": "test_pswd1"
        }
    )
    assert result.status_code == HTTPStatus.CONFLICT


async def test__register__status__internal_error(
        client: AsyncClient,
):
    with patch.object(
        RegisterService,
        "create_user_with_outbox",
        AsyncMock(side_effect=RuntimeError("unexpected")),
    ):
        result = await client.post(
            f"{API_URL}register",
            json={
                "email": "new@example.com",
                "password": "test_pswd1",
            },
        )

    assert result.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
