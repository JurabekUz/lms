from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import get_settings
from app.db.init import close_database, init_database
from app.web.error_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_database()
    yield
    await close_database()


settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)
register_exception_handlers(app)
app.include_router(router, prefix=settings.api_prefix)
