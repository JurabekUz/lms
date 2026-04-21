from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "academic-service"
    app_env: str = "local"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    api_prefix: str = "/api"
    database_url: str = "postgres://postgres:postgres@localhost:5432/lms_academic"
    identity_service_base_url: str = "http://localhost:8001"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
