import logging
import uuid
from datetime import datetime

import bcrypt
from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.user import UserRequestCreate, UserStatusUpdate
from src.db.tables import UserTable
from src.db.user_statuses import UserStatuses
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import EntityAlreadyExistsException
from src.services.outbox import OutBoxService


logger = logging.getLogger(__name__)


class RegisterService:
    """Service for user registration with outbox event support."""

    def __init__(
            self,
            session: AsyncSession,
            outbox_service: OutBoxService,
    ) -> None:
        self.__session = session
        self.__outbox_service = outbox_service


    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain-text password using bcrypt."""
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        return hashed_password

    async def _get_user_by_email(self, email: EmailStr) -> UserTable:
        """Get user by email."""
        user_stmt = (
            select(UserTable)
            .where(UserTable.email == email)
        )
        try:
            user_result = await self.__session.execute(user_stmt)
            user = user_result.scalar_one()
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise e

    async def _create_or_update_user(
        self,
        user_id: uuid.UUID,
        email: EmailStr,
        hashed_password: str,
    ) -> UserTable | None:
        """Create new user or update existing FAILED user."""
        stmt = (
            insert(UserTable)
            .values(
                id=user_id,
                email=email,
                password_hash=hashed_password,
                status=UserStatuses.PENDING.value,
            )
            .on_conflict_do_update(
                index_elements=["email"],
                set_={"status": UserStatuses.PENDING.value},
                where=UserTable.status == UserStatuses.FAILED.value,
            )
            .returning(UserTable)
        )

        result = await self.__session.execute(stmt)
        return result.scalar_one_or_none()

    async def _validate_existing_user(self, email: EmailStr) -> None:
        """Validate user status before registration."""
        existing_user = await self._get_user_by_email(email)

        if existing_user is None:
            return

        status = existing_user.status

        if status == UserStatuses.PENDING.value:
            raise EntityAlreadyExistsException(
                message="User registration is already in progress. Please wait."
            )
        elif status == UserStatuses.ACTIVE.value:
            raise EntityAlreadyExistsException(
                message="User already registered and active."
            )
        else:
            raise EntityAlreadyExistsException(
                message=f"User exists with status: {status}"
            )

    async def _handle_upsert_conflict(
            self,
            user_data: UserRequestCreate,
            user_id: uuid.UUID,
            hashed_password: str,
    ) -> UserTable:
        """Handle user upsert with conflict resolution."""
        user = await self._create_or_update_user(
            user_id=user_id,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        if user is None:
            await self._validate_existing_user(user_data.email)
            raise RuntimeError("Unexpected error during user creation")

        return user

    async def create_user_with_outbox(self, user_data: UserRequestCreate) -> UserTable:
        """Create user and outbox event in single transaction."""
        hashed_password = self.hash_password(user_data.password)
        user_id = uuid.uuid4()
        event_id = uuid.uuid4()

        try:
            user = await self._handle_upsert_conflict(
                user_data=user_data,
                user_id=user_id,
                hashed_password=hashed_password,
            )

            await self.__outbox_service.create_event(
                session=self.__session,
                event_id=event_id,
                user_id=str(user.id),
                user_data=user_data,
            )

            await self.__session.commit()
            logger.info(f"User {user.id} created with outbox event {event_id}")
            return user

        except IntegrityError as e:
            await self.__session.rollback()
            logger.error(f"Failed to register user: {e}")
            raise EntityAlreadyExistsException(
                message=ErrorMessages.USER_ALREADY_EXISTS
            ) from e

    async def get_user_status(self, user_id: str) -> UserTable | None:
        """Get user by ID."""
        stmt = select(UserTable).where(UserTable.id == uuid.UUID(user_id))
        result = await self.__session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_status(self, user_data: UserStatusUpdate) -> None:
        """Update user status."""
        stmt = (
            update(UserTable)
            .where(UserTable.id == user_data.user_id)
            .values(
                status=user_data.status,
                completed_at=datetime.now(),
            )
        )

        try:
            await self.__session.execute(stmt)
            await self.__session.commit()
            logger.info(f"User {user_data.user_id} status updated to {user_data.status}")
        except Exception as e:
            await self.__session.rollback()
            logger.error(f"Failed to update status for {user_data.user_id}: {e}")
            raise
