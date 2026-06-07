import logging
from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from src.api.schemas.user import (
    RolesUpdateSchema,
    UserProfileListSchema,
    UserProfileSchema,
)
from src.api.utils import check_permissions
from src.db.tables import UserProfileTable
from src.db.user_roles import UserRoles
from src.exceptions.user import NoRightsException
from src.services.user_service import UserProfileService


logger = logging.getLogger(__name__)

users_router = APIRouter(
    route_class=DishkaRoute,
    prefix="/users",
    tags=["users"],
)

@users_router.get("")
async def fetch_user_list(
        user_service: FromDishka[UserProfileService],
        current_user: FromDishka[UserProfileTable],
):
    try:
        check_permissions(current_roles=current_user.roles)
    except NoRightsException:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="No permissions")
    user_list = await user_service.fetch_user_list()
    return UserProfileListSchema(users=user_list or [])


@users_router.get("/me")
async def fetch_current_user(
        current_user: FromDishka[UserProfileTable],
):
    return UserProfileSchema.model_validate(current_user)


@users_router.get("/{user_id}")
async def fetch_user_by_id(
        user_service: FromDishka[UserProfileService],
        current_user: FromDishka[UserProfileTable],
        user_id: str,
):
    try:
        check_permissions(current_roles=current_user.roles)
    except NoRightsException:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="No permissions")
    if user_profile := await user_service.fetch_user_by_id(user_id=user_id):
        return UserProfileSchema.model_validate(user_profile)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"User {user_id} not found")


@users_router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user_by_id(
        user_service: FromDishka[UserProfileService],
        current_user: FromDishka[UserProfileTable],
        user_id: str,
):
    try:
        check_permissions(current_roles=current_user.roles, possible_roles=(UserRoles.ROLE_ADMIN, ))
    except NoRightsException:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="No permissions")
    await user_service.delete_user_profile(user_id=user_id)

@users_router.patch("/{user_id}")
async def update_user_roles_by_id(
        user_id: str,
        roles_data: RolesUpdateSchema,
        user_service: FromDishka[UserProfileService],
):

    updated_user = await user_service.update_user_roles(user_id=user_id, roles=roles_data.roles)
    if updated_user:
        return UserProfileSchema.model_validate(updated_user)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
