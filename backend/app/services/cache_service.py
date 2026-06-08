import json
from datetime import datetime, timezone

from app.core.redis import get_redis

CACHE_TTLS: dict[str, int] = {
    "price": 900,
    "fundamentals": 21600,
    "dividends": 21600,
    "company_info": 86400,
    "analyst_ratings": 86400,
    "insider": 86400,
    "earnings": 86400,
    "news": 1800,
    "technical": 900,
}


class CacheService:

    @staticmethod
    def build_key(provider: str, method: str, ticker: str) -> str:
        return f"cache:{provider}:{method}:{ticker.upper()}"

    async def get(self, key: str) -> dict | None:
        client = await get_redis()
        raw = await client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(
        self, key: str, value: dict, data_type: str
    ) -> None:
        client = await get_redis()
        ttl = CACHE_TTLS.get(data_type, 300)
        value["_cached_at"] = datetime.now(timezone.utc).isoformat()
        await client.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        client = await get_redis()
        await client.delete(key)

    async def get_or_fetch(
        self,
        key: str,
        data_type: str,
        fetch_fn,
    ) -> dict:
        cached = await self.get(key)
        if cached is not None:
            return {"data": cached, "cached": True}

        result = await fetch_fn()
        await self.set(key, result, data_type)
        return {"data": result, "cached": False}
