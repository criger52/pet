import uuid
from datetime import datetime

from sqlalchemy import JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all auth service ORM models."""


class UserTable(Base):
    """Represents a registered user with credentials."""

    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    error_message: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)


class OutBoxTable(Base):
    """Stores domain events for reliable outbox-based publishing."""

    __tablename__ = "outbox"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[uuid.UUID] = mapped_column(nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(nullable=True)
    retries: Mapped[int] = mapped_column(default=0, nullable=False)
