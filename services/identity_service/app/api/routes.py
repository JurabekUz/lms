from fastapi import APIRouter

from app.api.auth_routes import router as auth_router
from app.api.user_routes import router as users_router
from app.schemas.common import HealthResponse

api_router = APIRouter()
system_router = APIRouter(tags=["system"])


@system_router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", service="identity-service")


@system_router.get("/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    return HealthResponse(status="ready", service="identity-service")


api_router.include_router(system_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
