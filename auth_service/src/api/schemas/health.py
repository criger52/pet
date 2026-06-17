from src.api.schemas.base import BaseSchema


class HealthSchema(BaseSchema):
    """Response schema for the health check endpoint."""

    is_alive: bool
