from src.api.schemas.base import BaseSchema


class HealthSchema(BaseSchema):
    is_alive: bool