from src.exceptions.base import BaseCustomException


class EntityAlreadyExistsException(BaseCustomException):
    """Raised when attempting to create a user that already exists."""


class LoginFailedException(BaseCustomException):
    """Raised when login credentials are invalid."""
