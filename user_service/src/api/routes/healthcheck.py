import logging
from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from src.api.schemas.health import HealthSchema
from src.services.healthcheck import HealthCheckService


logger = logging.getLogger(__name__)

health_router = APIRouter(
    route_class=DishkaRoute,
)


@health_router.get("/health")
async def fetch_health(
        healthcheck_service: FromDishka[HealthCheckService],
) -> HealthSchema:
    """Return service liveness status based on database connectivity."""
    if await healthcheck_service.health_check():
        return HealthSchema(is_alive=True)
    logger.warning("Health check failed: database unavailable")
    raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE)
