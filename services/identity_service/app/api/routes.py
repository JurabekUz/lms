"""
API router composition for the identity-service.

We keep a single `api_router` here, then attach feature routers (auth, users, etc).
`main.py` mounts this router under `settings.api_prefix`, so paths here are relative
to that prefix (default: `/api`).
"""

from fastapi import APIRouter

from app.api.auth_routes import router as auth_router
from app.api.user_routes import router as users_router
from app.api.school_routes import router as school_router
from app.schemas.common import HealthResponse

# Root router that groups all service routes (it gets included from `main.py`).
api_router = APIRouter()

# Small internal/system endpoints (health/ready) live under a separate router
# to keep tags and responsibilities clear.
system_router = APIRouter(tags=["system"])


@system_router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    """Basic liveness probe (service is running and can respond)."""
    return HealthResponse(status="ok", service="identity-service")


@system_router.get("/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    """
    Readiness probe.

    If you later add checks (DB/Redis connectivity), this is the right endpoint
    to extend.
    """
    return HealthResponse(status="ready", service="identity-service")


# Router wiring order doesn't matter much, but keeping system first helps discoverability.
api_router.include_router(system_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(school_router)
