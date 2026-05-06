from auth_service.src.api.schemas.base import BaseSchema


class HealthSchema(BaseSchema):
    is_alive: bool