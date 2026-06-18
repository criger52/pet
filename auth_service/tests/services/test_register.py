import uuid
from typing import Callable

import pytest

from src.api.schemas.user import UserRequestCreate, UserStatusUpdate
from src.db.user_statuses import UserStatuses
from src.exceptions.user import EntityAlreadyExistsException
from src.services.register import RegisterService


async def test__register_service__create__ok(
        register_service: RegisterService,
) -> None:
    user_data = UserRequestCreate(email="test@example.com", password="test_pswd1")
    assert await register_service.create_user_with_outbox(user_data=user_data)

async def test__register_service__create__conflict(
        register_service: RegisterService,
        create_user_table: Callable
):

    user_data = UserRequestCreate(email="test@example.com", password="test_pswd1")
    await create_user_table(email=user_data.email, password=user_data.password)
    with pytest.raises(EntityAlreadyExistsException):
        await register_service.create_user_with_outbox(user_data=user_data)

async def test__register_service__get_user_status__not_found(
        register_service: RegisterService,
) -> None:
    user_id = str(uuid.uuid4())
    user = await register_service.get_user_status(user_id)

    assert user is None


async def test__register_service__update_user_status__ok(
        register_service: RegisterService,
        create_user_table,
) -> None:
    user = await create_user_table(status=UserStatuses.PENDING.value)

    user_data = UserStatusUpdate(
        user_id=user.id,
        status=UserStatuses.ACTIVE.value,
    )

    await register_service.update_user_status(user_data)

    updated_user = await register_service.get_user_status(str(user.id))
    assert updated_user.status == UserStatuses.ACTIVE.value
    assert updated_user.completed_at is not None
