import uuid

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi_admin import constants
from fastapi_admin.app import app as admin_app
from fastapi_admin.depends import get_redis
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.template import templates
from fastapi_admin.utils import check_password, hash_password
from redis.asyncio import Redis, from_url
from starlette import status

from app.admin import resources  # noqa: F401
from app.config.settings import get_settings
from app.models import AdminAccount


class SafeUsernamePasswordProvider(UsernamePasswordProvider):
    async def pre_save_admin(self, _, instance: AdminAccount, using_db, update_fields) -> None:
        db_obj = await self.admin_model.get_or_none(pk=instance.pk) if instance.pk else None
        if db_obj and db_obj.password == instance.password:
            return
        instance.password = hash_password(instance.password)

    async def login(self, request: Request, redis: Redis = Depends(get_redis)):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        remember_me = form.get("remember_me")
        admin = await self.admin_model.get_or_none(username=username)
        if not admin or not check_password(password, admin.password):
            return templates.TemplateResponse(
                self.template,
                status_code=status.HTTP_401_UNAUTHORIZED,
                context={"request": request, "error": "login_failed"},
            )

        response = RedirectResponse(url=request.app.admin_path, status_code=status.HTTP_303_SEE_OTHER)
        if remember_me == "on":
            expire = 3600 * 24 * 30
            response.set_cookie("remember_me", "on")
        else:
            expire = 3600
            response.delete_cookie("remember_me")

        token = uuid.uuid4().hex
        response.set_cookie(
            self.access_token,
            token,
            expires=expire,
            path=request.app.admin_path,
            httponly=True,
        )
        await redis.set(constants.LOGIN_USER.format(token=token), str(admin.pk), ex=expire)
        return response


async def configure_admin(application: FastAPI) -> None:
    settings = get_settings()
    redis: Redis = from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    provider = SafeUsernamePasswordProvider(
        admin_model=AdminAccount,
        login_logo_url=settings.admin_login_logo_url,
        login_title=f"{settings.app_name} admin",
    )
    await admin_app.configure(
        redis=redis,
        admin_path=settings.admin_path,
        logo_url=settings.admin_logo_url,
        providers=[provider],
    )
    application.state.admin_redis = redis


async def close_admin(application: FastAPI) -> None:
    redis: Redis | None = getattr(application.state, "admin_redis", None)
    if redis is not None:
        await redis.aclose()


def mount_admin(application: FastAPI) -> None:
    admin_path = get_settings().admin_path
    if any(getattr(route, "path", None) == admin_path for route in application.router.routes):
        return
    application.mount(admin_path, admin_app)
