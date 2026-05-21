from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from src.api.schemas.health import HealthSchema
from src.services.healthcheck import HealthCheckService


health_router = APIRouter(
    route_class=DishkaRoute,
)

@health_router.get("/health")
async def fetch_health(
        healthcheck_service: FromDishka[HealthCheckService],
) -> HealthSchema:
    if await healthcheck_service.health_check():
        return HealthSchema(is_alive=True)
    raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE)
