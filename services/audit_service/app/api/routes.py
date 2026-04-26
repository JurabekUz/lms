from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "audit-service"}


@router.get("/ready")
async def ready() -> dict:
    return {"status": "ready", "service": "audit-service"}
