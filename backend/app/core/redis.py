import aioredis
from app.core.config import settings


class RedisClient:
    _instance = None

    @classmethod
    async def get_client(cls):
        if cls._instance is None:
            cls._instance = aioredis.from_url(
                str(settings.REDIS_URL),
                decode_responses=True,
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def ping(cls):
        client = await cls.get_client()
        return await client.ping()
