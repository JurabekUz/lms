"""
FastAPI application entrypoint for `identity-service`.

This module wires together:
- Database initialization/teardown (Postgres via our ORM layer)
- Admin panel initialization (fastapi-admin) and mounting at `settings.admin_path`
- Public API routers mounted under `settings.api_prefix`
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin.setup import close_admin, configure_admin, mount_admin
from app.api.routes import api_router
from app.config.settings import get_settings
from app.db.init import close_database, init_database
from app.web.error_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    FastAPI lifespan hook.

    Runs once on startup and once on shutdown.
    We use it to:
    - connect/init the database
    - configure the admin panel (needs Redis + DB models)
    - close admin resources and DB connections on shutdown
    """
    await init_database()
    await configure_admin(application)
    yield
    await close_admin(application)
    await close_database()


settings = get_settings()

# Main ASGI application instance (uvicorn/gunicorn imports `app` from here).
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.app_debug,
    lifespan=lifespan,
)

# Centralized exception handlers (HTTP errors, validation errors, etc).
register_exception_handlers(app)

# Mount admin panel at `settings.admin_path` (default: `/admin`).
mount_admin(app)

# Mount REST API routes under `settings.api_prefix` (default: `/api`).
app.include_router(api_router, prefix=settings.api_prefix)
