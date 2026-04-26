from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "audit-service"
    app_env: str = "local"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8003
    api_prefix: str = "/api"

    database_url: str = "postgres://postgres:postgres@localhost:5434/lms_audit"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "lms.events"
    rabbitmq_dlx_exchange: str = "lms.events.dlx"
    rabbitmq_queue: str = "audit.q"
    rabbitmq_dlq: str = "audit.dlq"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
