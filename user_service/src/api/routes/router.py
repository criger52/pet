from fastapi import APIRouter

from src.api.routes.healthcheck import health_router

user_router = APIRouter(prefix="/api/v1/user", tags=["user"])
user_router.include_router(health_router)