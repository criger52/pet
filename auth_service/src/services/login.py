import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from dishka import FromDishka
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.user import LoginRequest, LoginResponse
from src.config import Settings
from src.db.tables import UserTable
from src.db.user_statuses import UserStatuses
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import LoginFailedException


logger = logging.getLogger(__name__)


class LoginService:
    """Handles user authentication and JWT token generation."""

    def __init__(self, session: FromDishka[AsyncSession], settings: Settings):
        self.__session = session
        self._setting = settings

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        """Verify a plain-text password against a bcrypt hash."""
        return bcrypt.checkpw(plain_password.encode(), password_hash.encode())

    def _create_access_token(self, user_id: str) -> str:
        """Create a short-lived JWT access token for the given user."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._setting.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": user_id, "type": "access", "exp": expire}
        return jwt.encode(payload, self._setting.JWT_SECRET_KEY, algorithm=self._setting.JWT_ALGORITHM)

    def _create_refresh_token(self, user_id: str) -> str:
        """Create a long-lived JWT refresh token for the given user."""
        expire = datetime.now(timezone.utc) + timedelta(days=self._setting.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"sub": user_id, "type": "refresh", "exp": expire}
        return jwt.encode(payload, self._setting.JWT_SECRET_KEY, algorithm=self._setting.JWT_ALGORITHM)

    async def login(self, user_credentials: LoginRequest) -> LoginResponse:
        """Authenticate user credentials and return access and refresh tokens."""
        result = await self.__session.execute(
            select(UserTable).
            where(
                UserTable.email == user_credentials.email,
                UserTable.status == UserStatuses.ACTIVE,
            )
        )
        user = result.scalar_one_or_none()

        if not user or not self.verify_password(user_credentials.password, user.password_hash):
            logger.warning(f"Invalid credentials for email={user_credentials.email}")
            raise LoginFailedException(message=ErrorMessages.INVALID_CREDENTIALS.value)

        logger.info(f"User authenticated: user_id={user.id}")
        return LoginResponse(
            access_token=self._create_access_token(user_id=str(user.id)),
            refresh_token=self._create_refresh_token(user_id=str(user.id)),
        )
