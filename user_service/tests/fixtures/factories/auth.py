from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from src.config import Settings
from src.db.tables import UserProfileTable


@pytest.fixture
async def create_auth_headers(
        settings: Settings,
):

    async def _create_auth_headers(
            user_profile: UserProfileTable
    ) -> dict:
        payload = {
            "sub": f"{user_profile.user_id}",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return {
            "Authorization": f"Bearer {token}",
        }

    return _create_auth_headers