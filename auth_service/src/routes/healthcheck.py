from fastapi import APIRouter, Depends
from src.services.healthcheck import (HealthCheckService,
                                      get_health_check_service)

health_router = APIRouter()

@health_router.get("/health")
async def fetch_health(
        healthcheck_service: HealthCheckService = Depends(get_health_check_service)
) -> bool:
    return await healthcheck_service.health_check()
