from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "identity-service"
    app_env: str = "local"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    api_prefix: str = "/api/v1"
    database_url: str = "postgres://postgres:postgres@localhost:5432/lms_identity"
    redis_url: str = "redis://localhost:6379/0"
    admin_path: str = "/admin"
    admin_logo_url: str | None = None
    admin_login_logo_url: str | None = None
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
