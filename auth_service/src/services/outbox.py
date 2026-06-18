import logging
import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import delete, insert, select, update

from src.db.tables import OutBoxTable


logger = logging.getLogger(__name__)


class EventType(StrEnum):
    """Supported outbox event types."""

    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"


class OutBoxService:
    """Manages outbox events for at-least-once delivery to Kafka."""

    async def create_event(
            self,
            session,
            event_id: uuid.UUID,
            user_id,
            user_data,
    ) -> OutBoxTable:
        """Insert a new outbox event within the current transaction."""
        stmt = (
            insert(OutBoxTable)
            .values(
                event_id=event_id,
                event_type=EventType.USER_CREATED.value,
                aggregate_id=user_id,
                payload={
                    "user_id": str(user_id),
                    "email": user_data.email,
                    "event_id": str(event_id),
                }
            )
            .returning(OutBoxTable)
        )
        try:
            result = await session.execute(stmt)
            await session.commit()
            logger.info(f"Outbox event created: event_id={event_id} user_id={user_id}")
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Failed to create outbox event event_id={event_id}: {e}")
            raise e

    async def get_unprocessed_events(self, session, limit: int = 100):
        """Fetch unprocessed outbox events ordered by creation time."""
        stmt = (
            select(OutBoxTable)
            .where(OutBoxTable.processed_at.is_(None))
            .order_by(OutBoxTable.created_at.asc())
            .limit(limit)
        )
        try:
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to fetch unprocessed events: {e}")

    async def mark_as_processed(
            self,
            session,
            event_id: int,
    ):
        """Mark an outbox event as successfully processed."""
        stmt = (
            update(OutBoxTable)
            .where(OutBoxTable.id == event_id)
            .values(
                processed_at=datetime.now(),
            )
        )
        try:
            await session.execute(stmt)
            await session.commit()
            logger.debug(f"Event {event_id} marked as processed")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to mark event {event_id} as processed: {e}")

    async def increment_retries(
            self,
            session,
            event_id: int
    ):
        """Increment the retry counter for a failed outbox event."""
        stmt = (
            update(OutBoxTable)
            .where(OutBoxTable.id == event_id)
            .values(retries=OutBoxTable.retries + 1)
        )
        try:
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to increment retries for event {event_id}: {e}")

    async def delete_event(
            self,
            session,
            event_id: int
    ):
        """Delete an outbox event after exceeding max retries."""
        stmt = delete(OutBoxTable).where(OutBoxTable.id == event_id)
        try:
            await session.execute(stmt)
            await session.commit()
            logger.warning(f"Outbox event {event_id} deleted")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to delete event {event_id}: {e}")
