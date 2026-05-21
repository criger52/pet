import uuid

from pydantic import EmailStr

from src.api.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str

class UserResponse(BaseSchema):
    id: uuid.UUID
    email: EmailStr

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class LoginResponse(BaseSchema):
    access_token: str
    refresh_token: str