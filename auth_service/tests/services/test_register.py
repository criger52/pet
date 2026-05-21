from typing import Callable
from unittest.mock import AsyncMock, patch

import pytest

from src.api.schemas.user import UserCreate
from src.exceptions.user import EntityAlreadyExistsException
from src.services.register import RegisterService


async def test__register_service__create__ok(
        register_service: RegisterService,
) -> None:
    user_data = UserCreate(email="test@example.com", password="test_pswd1")
    with patch("src.broker.producer.KafkaProducer", new_callable=AsyncMock):
        assert await register_service.create_user(user_data=user_data)

async def test__register_service__create__conflict(
        register_service: RegisterService,
        create_user_table: Callable
):

    user_data = UserCreate(email="test@example.com", password="test_pswd1")
    await create_user_table(email=user_data.email, password=user_data.password)
    with patch("src.broker.producer.KafkaProducer", new_callable=AsyncMock):
        with pytest.raises(EntityAlreadyExistsException):
            await register_service.create_user(user_data=user_data)
