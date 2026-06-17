from enum import StrEnum


class UserRoles(StrEnum):
    """Available user roles in the system."""

    ROLE_USER = "user"
    ROLE_ADMIN = "admin"
    ROLE_MANAGER = "manager"
