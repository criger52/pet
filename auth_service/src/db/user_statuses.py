from enum import StrEnum


class UserStatuses(StrEnum):
    """Available user status in the system."""

    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
