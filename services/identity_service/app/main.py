from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin.setup import close_admin, configure_admin, mount_admin
from app.api.routes import api_router
from app.config.settings import get_settings
from app.db.init import close_database, init_database
from app.web.error_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_database()
    await configure_admin(application)
    yield
    await close_admin(application)
    await close_database()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.app_debug,
    lifespan=lifespan,
)
register_exception_handlers(app)
mount_admin(app)
app.include_router(api_router, prefix=settings.api_prefix)
