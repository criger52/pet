class BaseCustomException(Exception):
    """Base exception that carries a user-facing error message."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
