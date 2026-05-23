from enum import StrEnum


class UserRoles(StrEnum):
    ROLE_USER = "user"
    ROLE_ADMIN = "admin"
    ROLE_MANAGER = "manager"