import uuid
from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.db.user_roles import UserRoles


class Base(DeclarativeBase):
    """Base class for all user service ORM models."""


class UserProfileTable(Base):
    """Represents a user profile linked to an auth service user."""

    __tablename__ = "user_profiles"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=[UserRoles.ROLE_USER.value])
