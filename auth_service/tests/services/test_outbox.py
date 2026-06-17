import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.user import UserRequestCreate
from src.db.tables import OutBoxTable
from src.services.outbox import EventType, OutBoxService


async def test__outbox_service__create_event__ok(
        session: AsyncSession,
        outbox_service: OutBoxService,
) -> None:
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    user_data = UserRequestCreate(
        email="test@example.com",
        password="SecurePass123!",
    )

    event = await outbox_service.create_event(
        session=session,
        event_id=event_id,
        user_id=user_id,
        user_data=user_data,
    )

    assert event is not None
    assert event.event_id == event_id
    assert event.event_type == EventType.USER_CREATED.value
    assert event.aggregate_id == user_id
    assert event.payload["user_id"] == str(user_id)
    assert event.payload["email"] == "test@example.com"
    assert event.retries == 0
    assert event.processed_at is None


async def test__outbox_service__get_unprocessed_events__ok(
        session: AsyncSession,
        outbox_service: OutBoxService,
) -> None:
    user_data = UserRequestCreate(
        email="test@example.com",
        password="SecurePass123!",
    )

    for i in range(3):
        event_id = uuid.uuid4()
        user_id = uuid.uuid4()
        await outbox_service.create_event(
            session=session,
            event_id=event_id,
            user_id=user_id,
            user_data=user_data,
        )

    events = await outbox_service.get_unprocessed_events(session, limit=10)

    assert len(events) >= 3
    assert all(e.processed_at is None for e in events[:3])


async def test__outbox_service__mark_as_processed__ok(
        session: AsyncSession,
        outbox_service: OutBoxService,
) -> None:
    user_data = UserRequestCreate(
        email="test@example.com",
        password="SecurePass123!",
    )
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()

    event = await outbox_service.create_event(
        session=session,
        event_id=event_id,
        user_id=user_id,
        user_data=user_data,
    )

    await outbox_service.mark_as_processed(session, event.id)

    events = await outbox_service.get_unprocessed_events(session, limit=10)
    assert event.id not in [e.id for e in events]


async def test__outbox_service__increment_retries__ok(
        session: AsyncSession,
        outbox_service: OutBoxService,
) -> None:
    user_data = UserRequestCreate(
        email="test@example.com",
        password="SecurePass123!",
    )
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()

    event = await outbox_service.create_event(
        session=session,
        event_id=event_id,
        user_id=user_id,
        user_data=user_data,
    )

    assert event.retries == 0

    await outbox_service.increment_retries(session, event.id)

    stmt = select(OutBoxTable).where(OutBoxTable.id == event.id)
    result = await session.execute(stmt)
    updated_event = result.scalar_one()

    assert updated_event.retries == 1


async def test__outbox_service__delete_event__ok(
        session: AsyncSession,
        outbox_service: OutBoxService,
) -> None:
    user_data = UserRequestCreate(
        email="test@example.com",
        password="SecurePass123!",
    )
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()

    event = await outbox_service.create_event(
        session=session,
        event_id=event_id,
        user_id=user_id,
        user_data=user_data,
    )

    await outbox_service.delete_event(session, event.id)

    stmt = select(OutBoxTable).where(OutBoxTable.id == event.id)
    result = await session.execute(stmt)
    deleted_event = result.scalar_one_or_none()

    assert deleted_event is None


async def test__outbox_service__get_unprocessed_events__empty(
        session: AsyncSession,
        outbox_service: OutBoxService,
) -> None:
    events = await outbox_service.get_unprocessed_events(session, limit=10)
    assert len(events) == 0
