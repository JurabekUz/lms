from redis.asyncio import Redis, from_url

StrictRedis = Redis


async def create_redis_pool(url: str, encoding: str | None = None, **kwargs) -> Redis:
    decode_responses = kwargs.pop("decode_responses", bool(encoding))
    return from_url(url, encoding=encoding, decode_responses=decode_responses, **kwargs)
