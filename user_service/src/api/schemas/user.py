from datetime import datetime
from uuid import UUID

from src.api.schemas.base import BaseSchema
from src.db.user_roles import UserRoles


class UserProfileSchema(BaseSchema):
    """Response schema for a single user profile."""

    id: UUID
    user_id: UUID
    roles: list[UserRoles]
    created_at: datetime


class UserProfileListSchema(BaseSchema):
    """Response schema for a list of user profiles."""

    users: list[UserProfileSchema]


class RolesUpdateSchema(BaseSchema):
    """Request schema for updating user roles."""

    roles: list[UserRoles]
