import logging
from typing import Sequence

from fastapi import HTTPException
from jose import JWTError, jwt

from src.config import Settings
from src.db.user_roles import UserRoles
from src.exceptions.user import NoRightsException


logger = logging.getLogger(__name__)

def check_permissions(
    current_roles: Sequence[UserRoles],
    possible_roles: Sequence[UserRoles] | None = None,
) -> None:
    if not possible_roles:
        possible_roles = (UserRoles.ROLE_ADMIN, UserRoles.ROLE_MANAGER)
    if not set(current_roles) & set(possible_roles):
        raise NoRightsException("No permissions")

def decode_token(
        token: str,
        settings: Settings,
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY)
        user_id: str = payload["sub"]
        if not user_id:
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    except Exception as e:
        logger.error(e)
        raise e