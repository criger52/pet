from enum import StrEnum


class ErrorMessages(StrEnum):
    """Enumeration of API error message strings."""

    USER_ALREADY_EXISTS = "User Already Exists"
    UNKNOWN_ERROR = "Unknown Error"
    INVALID_CREDENTIALS = "Invalid Credentials"
