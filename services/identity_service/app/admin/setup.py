import uuid

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi_admin import constants
from fastapi_admin.app import app as admin_app
from fastapi_admin.depends import get_redis
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.template import templates
from passlib.context import CryptContext
from redis.asyncio import Redis, from_url
from starlette import status

from app.admin import resources  # noqa: F401
from app.config.settings import get_settings
from app.models import AdminAccount


_pwd_context = CryptContext(
    # `bcrypt_sha256` supports long passwords (bcrypt alone truncates at 72 bytes).
    schemes=["bcrypt"],
    deprecated="auto",
)


def _normalize_admin_path(admin_path: str) -> str:
    """
    Normalize admin mount path.

    We keep mount path without trailing slash (Starlette `mount("/admin", ...)`),
    but we often want to redirect users to `/admin/` after login so the mounted app
    receives a proper root path (`/`) instead of an empty path (which can yield 404
    depending on the sub-app router).
    """
    admin_path = (admin_path or "/").strip()
    if not admin_path.startswith("/"):
        admin_path = "/" + admin_path
    # Avoid treating "/admin/" and "/admin" as different paths.
    if admin_path != "/":
        admin_path = admin_path.rstrip("/")
    return admin_path


def _first_model_resource_name(resources) -> str | None:
    """
    Return the first model resource name used by fastapi-admin routes.

    fastapi-admin model routes are addressed as `/{model_name_lower}/...`, where
    `model_name_lower` is the tortoise model class name lowercased.
    """
    for resource in resources or []:
        # Dropdowns contain nested resources.
        nested = getattr(resource, "resources", None)
        if nested:
            found = _first_model_resource_name(nested)
            if found:
                return found

        model = getattr(resource, "model", None)
        if model is not None:
            return getattr(model, "__name__", "").lower() or None
    return None


@admin_app.get("/")
async def admin_index(request: Request):
    """
    Admin landing page.

    fastapi-admin doesn't ship with a root (`/`) route by default, so `/admin/`
    would return 404 after a successful login redirect. We fix that by redirecting:
    - unauthenticated users -> `/admin/login`
    - authenticated users   -> first registered model list page
    """
    admin_path = _normalize_admin_path(getattr(request.app, "admin_path", "/admin"))
    if getattr(request.state, "admin", None) is None:
        return RedirectResponse(url=f"{admin_path}/login", status_code=status.HTTP_303_SEE_OTHER)

    first_model = _first_model_resource_name(getattr(request.app, "resources", []))
    if first_model:
        return RedirectResponse(
            url=f"{admin_path}/{first_model}/list",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(url=f"{admin_path}/login", status_code=status.HTTP_303_SEE_OTHER)


class SafeUsernamePasswordProvider(UsernamePasswordProvider):
    async def pre_save_admin(self, _, instance: AdminAccount, using_db, update_fields) -> None:
        db_obj = await self.admin_model.get_or_none(pk=instance.pk) if instance.pk else None
        if db_obj and db_obj.password == instance.password:
            return
        instance.password = _pwd_context.hash(instance.password)

    async def login(self, request: Request, redis: Redis = Depends(get_redis)):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        remember_me = form.get("remember_me")
        admin = await self.admin_model.get_or_none(username=username)
        try:
            password_ok = bool(admin) and _pwd_context.verify(password or "", admin.password)
        except ValueError:
            # Some bcrypt variants reject >72-byte passwords; treat as auth failure.
            password_ok = False

        if not password_ok:
            return templates.TemplateResponse(
                self.template,
                status_code=status.HTTP_401_UNAUTHORIZED,
                context={"request": request, "error": "login_failed"},
            )

        admin_path = _normalize_admin_path(getattr(request.app, "admin_path", "/admin"))
        # Redirect to a trailing-slash URL so the mounted admin sub-app sees `/` as its path.
        response = RedirectResponse(url=f"{admin_path}/", status_code=status.HTTP_303_SEE_OTHER)
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
            path=admin_path,
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
        admin_path=_normalize_admin_path(settings.admin_path),
        logo_url=settings.admin_logo_url,
        providers=[provider],
    )
    application.state.admin_redis = redis


async def close_admin(application: FastAPI) -> None:
    redis: Redis | None = getattr(application.state, "admin_redis", None)
    if redis is not None:
        await redis.aclose()


def mount_admin(application: FastAPI) -> None:
    admin_path = _normalize_admin_path(get_settings().admin_path)
    print(f"Mounting admin interface at {admin_path}")
    if any(getattr(route, "path", None) == admin_path for route in application.router.routes):
        print(f"Admin path '{admin_path}' is already in use. Skipping admin mount.")
        return
    application.mount(admin_path, admin_app)
