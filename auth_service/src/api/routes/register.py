import logging

from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.user import UserCreate, UserResponse
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import EntityAlreadyExistsException
from src.services.register_service import RegisterService, get_register_service

logger = logging.getLogger(__name__)
register_router = APIRouter()


@register_router.post("/register", response_model=UserResponse)
async def register(
        user_data: UserCreate,
        register_service: RegisterService = Depends(get_register_service)
):
    try:
        return await register_service.create_user(user_data)
    except EntityAlreadyExistsException as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorMessages.USER_ALREADY_EXISTS.value
        ) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail=ErrorMessages.UNKNOWN_ERROR.value
        ) from e
