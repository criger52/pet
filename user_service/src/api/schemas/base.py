from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with ORM support and immutable instances."""

    model_config = ConfigDict(from_attributes=True, frozen=True)
