import logging
from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from src.api.schemas.user import UserCreate, UserResponse
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import EntityAlreadyExistsException
from src.services.register import RegisterService


logger = logging.getLogger(__name__)
register_router = APIRouter(
    route_class=DishkaRoute,
)


@register_router.post("/register", response_model=UserResponse, status_code=201)
async def register(
        user_data: UserCreate,
        register_service: FromDishka[RegisterService]
):
    try:
        return await register_service.create_user(user_data)
    except EntityAlreadyExistsException as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=e.message
        ) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.UNKNOWN_ERROR.value
        ) from e
