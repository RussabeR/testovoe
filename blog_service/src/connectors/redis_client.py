import redis.asyncio as redis


class RedisManager:
    def __init__(self, client: redis.Redis):
        self.client = client

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str):
        await self.client.delete(key)
