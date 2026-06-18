import logging
from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from src.api.schemas.user import (
    RegistrationResponse,
    RegistrationStatusResponse,
    UserRequestCreate,
)
from src.db.user_statuses import UserStatuses
from src.exceptions.messages import ErrorMessages
from src.exceptions.user import EntityAlreadyExistsException
from src.services.register import RegisterService


logger = logging.getLogger(__name__)
register_router = APIRouter(
    route_class=DishkaRoute,
)


@register_router.post("/register", response_model=RegistrationResponse, status_code=202)
async def register(
        user_data: UserRequestCreate,
        register_service: FromDishka[RegisterService]
):
    """Register a new user and enqueue a user.created outbox event."""
    try:

        user = await register_service.create_user_with_outbox(user_data)
        
        logger.info(f"Registration initiated for: {user_data.email}, user_id={user.id}")
        response = RegistrationResponse(
                message="Registration in progress",
                user_id=str(user.id),
                status=UserStatuses.PENDING.value,
                check_status_url=f"/api/v1/auth/registration/{user.id}/status",
                created_at=user.created_at.isoformat() if user.created_at else None
            ).model_dump()

        return response
    except EntityAlreadyExistsException as e:
        logger.info(f"Registration conflict for {user_data.email}: {e.message}")
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=e.message
        ) from e
    except Exception as e:
        logger.error(f"Unexpected registration error for {user_data.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.UNKNOWN_ERROR.value
        ) from e


@register_router.get("/registration/{user_id}/status", response_model=RegistrationStatusResponse)
async def get_registration_status(
        user_id: str,
        register_service: FromDishka[RegisterService]
):
    """Check registration status."""
    user = await register_service.get_user_status(user_id)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found" # TODO: из enum
        )

    return RegistrationStatusResponse(
        user_id=str(user.id),
        status=user.status,
        created_at=user.created_at.isoformat() if user.created_at else None,
        completed_at=user.completed_at.isoformat() if user.completed_at else None,
        error=user.error_message if user.status == "failed" else None
    )
