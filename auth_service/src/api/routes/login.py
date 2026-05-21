import logging

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException
from starlette import status

from src.api.schemas.user import LoginRequest, LoginResponse
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import LoginFailedException
from src.services.login import LoginService


logger = logging.getLogger(__name__)
login_router = APIRouter(
    route_class=DishkaRoute,
)


@login_router.post("/login", response_model=LoginResponse)
async def login(
        user_data: LoginRequest,
        login_service: FromDishka[LoginService]
):
    try:
        tokens = await login_service.login(user_data)
        return tokens
    except LoginFailedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=500,
            detail=ErrorMessages.UNKNOWN_ERROR.value
        ) from e
