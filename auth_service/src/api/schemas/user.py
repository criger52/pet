import uuid

from pydantic import EmailStr

from src.api.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    """schema for user creation."""
    user_id: uuid.UUID
    email: EmailStr

class UserRequestCreate(BaseSchema):
    """Request schema for user registration."""

    email: EmailStr
    password: str

class UserStatusUpdate(BaseSchema):
    """Request schema for user status update."""
    user_id: uuid.UUID
    status: str


class UserResponse(BaseSchema):
    """Response schema for a registered user."""

    id: uuid.UUID
    email: EmailStr


class LoginRequest(BaseSchema):
    """Request schema for user login."""

    email: EmailStr
    password: str


class LoginResponse(BaseSchema):
    """Response schema containing JWT access and refresh tokens."""

    access_token: str
    refresh_token: str


class RegistrationResponse(BaseSchema):
    """Response for async registration."""
    message: str
    user_id: str
    status: str
    check_status_url: str
    created_at: str | None = None

class RegistrationStatusResponse(BaseSchema):
    """Response for registration status check."""
    user_id: str
    status: str
    created_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
