import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.tables import UserTable
from src.db.user_statuses import UserStatuses
from src.services.saga import SagaService


async def test__saga_service__handle_failed_registration__ok(
        session: AsyncSession,
        saga_service: SagaService,
        create_user_table,
) -> None:
    user = await create_user_table(status=UserStatuses.PENDING.value)

    error_message = "User creation failed in some service"
    await saga_service.handle_failed_registration(
        user_id=str(user.id),
        error=error_message,
    )

    await session.refresh(user)

    assert user.status == UserStatuses.FAILED.value
    assert user.error_message == error_message
    assert user.completed_at is not None


async def test__saga_service__handle_failed_registration__user_not_found(
        session: AsyncSession,
        saga_service: SagaService,
) -> None:
    non_existent_user_id = str(uuid.uuid4())

    await saga_service.handle_failed_registration(
        user_id=non_existent_user_id,
        error="Some error",
    )

    stmt = select(UserTable).where(UserTable.id == uuid.UUID(non_existent_user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    assert user is None


async def test__saga_service__handle_successful_registration__ok(
        session: AsyncSession,
        saga_service: SagaService,
        create_user_table,
) -> None:
    user = await create_user_table(status=UserStatuses.PENDING.value)

    await saga_service.handle_successful_registration(
        user_id=str(user.id),
    )

    await session.refresh(user)
    assert user.status == UserStatuses.ACTIVE.value
    assert user.completed_at is not None


async def test__saga_service__handle_successful_registration__user_not_found(
        session: AsyncSession,
        saga_service: SagaService,
) -> None:
    non_existent_user_id = str(uuid.uuid4())

    await saga_service.handle_successful_registration(
        user_id=non_existent_user_id,
    )

    stmt = select(UserTable).where(UserTable.id == uuid.UUID(non_existent_user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    assert user is None
