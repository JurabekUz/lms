from tortoise import Tortoise

from app.config.settings import get_settings


def get_tortoise_config() -> dict:
    settings = get_settings()
    return {
        "connections": {"default": settings.database_url},
        "apps": {
            "models": {
                "models": [
                    "app.models",
                ],
                "default_connection": "default",
            }
        },
    }


TORTOISE_ORM = get_tortoise_config()


async def init_database() -> None:
    await Tortoise.init(config=TORTOISE_ORM)


async def close_database() -> None:
    await Tortoise.close_connections()
