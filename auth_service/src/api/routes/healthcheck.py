from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.health import HealthSchema
from src.services.healthcheck import (HealthCheckService,
                                      get_healthcheck_service)

health_router = APIRouter()

@health_router.get("/health")
async def fetch_health(
        healthcheck_service: HealthCheckService = Depends(get_healthcheck_service),
) -> HealthSchema:
    if await healthcheck_service.health_check():
        return HealthSchema(is_alive=True)
    raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE)
