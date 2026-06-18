from enum import StrEnum


class MessageStatuses(StrEnum):
    """Available message status in the system."""
    FAILED = "failed"
    SUCCESS = "success"