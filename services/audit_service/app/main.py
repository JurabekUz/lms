from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import get_settings
from app.consumer.rabbit_consumer import RabbitConsumer
from app.db.init import close_database, init_database
from app.repositories.audit_repository import AuditRepository
from app.services.ingest_service import IngestService
from app.web.error_handlers import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_database()
    consumer = RabbitConsumer(settings=settings, ingest_service=IngestService(audit_repository=AuditRepository()))
    await consumer.start()
    application.state.consumer = consumer
    yield
    app_consumer = getattr(application.state, "consumer", None)
    if app_consumer is not None:
        await app_consumer.close()
    await close_database()


app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)
register_exception_handlers(app)
app.include_router(router, prefix=settings.api_prefix)
