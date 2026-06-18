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
    """Return a list of all user profiles (admin/manager only)."""
    try:
        check_permissions(current_roles=current_user.roles)
    except NoRightsException:
        logger.warning("Forbidden: user %s lacks permissions to list users", current_user.user_id)
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="No permissions")
    user_list = await user_service.fetch_user_list()
    logger.info("User list fetched by %s, count=%s", current_user.user_id, len(user_list or []))
    return UserProfileListSchema(users=user_list or [])


@users_router.get("/me")
async def fetch_current_user(
        current_user: FromDishka[UserProfileTable],
):
    """Return the profile of the currently authenticated user."""
    return UserProfileSchema.model_validate(current_user)


@users_router.get("/{user_id}")
async def fetch_user_by_id(
        user_service: FromDishka[UserProfileService],
        current_user: FromDishka[UserProfileTable],
        user_id: str,
):
    """Return a user profile by ID (admin/manager only)."""
    try:
        check_permissions(current_roles=current_user.roles)
    except NoRightsException:
        logger.warning("Forbidden: user %s lacks permissions to fetch user %s", current_user.user_id, user_id)
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="No permissions")
    if user_profile := await user_service.fetch_user_by_id(user_id=user_id):
        return UserProfileSchema.model_validate(user_profile)
    logger.info("User not found: user_id=%s", user_id)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"User {user_id} not found")


@users_router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user_by_id(
        user_service: FromDishka[UserProfileService],
        current_user: FromDishka[UserProfileTable],
        user_id: str,
):
    """Delete a user profile by ID (admin only)."""
    try:
        check_permissions(current_roles=current_user.roles, possible_roles=(UserRoles.ROLE_ADMIN, ))
    except NoRightsException:
        logger.warning("Forbidden: user %s lacks permissions to delete user %s", current_user.user_id, user_id)
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="No permissions")
    await user_service.delete_user_profile(user_id=user_id)
    logger.info("User %s deleted by %s", user_id, current_user.user_id)


@users_router.patch("/{user_id}")
async def update_user_roles_by_id(
        user_id: str,
        roles_data: RolesUpdateSchema,
        user_service: FromDishka[UserProfileService],
):
    """Update roles for a user profile by ID."""
    updated_user = await user_service.update_user_roles(user_id=user_id, roles=roles_data.roles)
    if updated_user:
        logger.info("Roles updated for user_id=%s: %s", user_id, roles_data.roles)
        return UserProfileSchema.model_validate(updated_user)
    logger.info("User not found for role update: user_id=%s", user_id)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
