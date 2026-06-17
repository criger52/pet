import logging

from dishka import FromDishka, Provider, Scope, provide
from fastapi import Request

from src.api.utils import decode_token
from src.config import Settings
from src.db.tables import UserProfileTable
from src.services.user_service import UserProfileService


logger = logging.getLogger(__name__)


class AuthProvider(Provider):
    """Resolves the current authenticated user from the JWT Bearer token."""

    def __init__(
            self,
            settings: Settings,
    ):
        super().__init__()
        self.__settings = settings

    @provide(scope=Scope.REQUEST)
    async def current_user(
        self,
        request: Request,
        user_service: FromDishka[UserProfileService],
    ) -> UserProfileTable:
        """Extract user ID from JWT and load the corresponding profile."""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        user_id = decode_token(token, self.__settings)
        logger.debug(f"Authenticated request from user_id={user_id}")
        return await user_service.fetch_user_by_id(user_id)
