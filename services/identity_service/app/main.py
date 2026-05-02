"""
FastAPI application entrypoint for `identity-service`.

This module wires together:
- Database initialization/teardown (Postgres via our ORM layer)
- Admin panel initialization (fastapi-admin) and mounting at `settings.admin_path`
- Public API routers mounted under `settings.api_prefix`
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin.setup import close_admin, configure_admin, mount_admin
from app.api.routes import api_router
from app.config.settings import get_settings
from app.db.init import close_database, init_database
from app.infra.event_publisher import NoopEventPublisher, RabbitMQEventPublisher
from app.infra.outbox_worker import OutboxWorker
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
    # rabbit mq ni ishlatamizmi yoki yoqmi deb tekshiramiz
    publisher = None
    if settings.rabbitmq_url:
        publisher = RabbitMQEventPublisher(
            url=settings.rabbitmq_url,
            exchange_name=settings.rabbitmq_exchange,
        )
        try:
            await publisher.connect()
            application.state.event_publisher = publisher
            
            # Outbox workerni alohida task sifatida ishga tushiramiz.
            # Bu worker bazadagi 'outbox_events'ni kuzatib MQ'ga chiqaradi.
            worker = OutboxWorker(publisher=publisher)
            application.state.outbox_worker = worker
            application.state.outbox_worker_task = asyncio.create_task(worker.run())
            
        except Exception as e:
            print(f"FAILED TO CONNECT TO RABBITMQ: {e}")
            application.state.event_publisher = NoopEventPublisher()
    yield
    # Shutdown jarayoni
    worker_task = getattr(application.state, "outbox_worker_task", None)
    if worker_task:
        # Workerga to'xtash haqida xabar beramiz va taskni kutamiz.
        application.state.outbox_worker.stop()
        await worker_task
    app_publisher = getattr(application.state, "event_publisher", None)
    if isinstance(app_publisher, RabbitMQEventPublisher):
        await app_publisher.close()
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
