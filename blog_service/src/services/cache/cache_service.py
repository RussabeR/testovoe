import json
from typing import Any, Callable, Awaitable

from src.connectors.redis_client import RedisManager


class BaseCacheService:
    def __init__(self, redis: RedisManager):
        self.redis = redis

    async def get(self, key: str):
        data = await self.redis.get(key)

        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: int):
        await self.redis.set(key, json.dumps(value), ttl)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str):
        keys = await self.redis.client.keys(pattern)
        if keys:
            await self.redis.client.delete(*keys)

    async def get_or_set(
        self,
        key: str,
        callback: Callable[[], Awaitable[Any]],
        ttl: int
    ):
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await callback()
        await self.set(key, value, ttl)
        return value