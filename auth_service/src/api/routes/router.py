from fastapi import APIRouter
from src.api.routes.healthcheck import health_router
from src.api.routes.register import register_router

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
auth_router.include_router(health_router)
auth_router.include_router(register_router)