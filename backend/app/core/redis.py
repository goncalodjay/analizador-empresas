from redis.asyncio import Redis

from app.core.config import settings

_redis = None


async def get_redis():
    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            str(settings.REDIS_URL),
            decode_responses=True,
        )
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


async def ping_redis():
    client = await get_redis()
    return await client.ping()
