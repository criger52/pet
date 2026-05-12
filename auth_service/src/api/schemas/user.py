from pydantic import EmailStr
from src.api.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str

class UserResponse(BaseSchema):
    id: int
    email: EmailStr
