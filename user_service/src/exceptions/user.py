from src.exceptions.base import BaseCustomException


class NoRightsException(BaseCustomException):
    """Raised when a user lacks the required permissions."""
