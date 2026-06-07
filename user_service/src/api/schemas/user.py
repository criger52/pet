from datetime import datetime
from uuid import UUID

from src.api.schemas.base import BaseSchema
from src.db.user_roles import UserRoles


class UserProfileSchema(BaseSchema):
    id: UUID
    user_id: UUID
    roles: list[UserRoles]
    created_at: datetime

class UserProfileListSchema(BaseSchema):
    users: list[UserProfileSchema]

class RolesUpdateSchema(BaseSchema):
    roles: list[UserRoles]
