from src.services.cache.cache_service import BaseCacheService
from src.config import settings


class PostsCacheService:

    def __init__(self, cache: BaseCacheService):
        self.cache = cache

    def _key_post(self, post_id: int) -> str:
        return f"post:{post_id}"

    def _key_user_post(self, user_id: int, post_id: int) -> str:
        return f"post:{post_id}:user:{user_id}"

    def _key_user_posts(self, user_id: int) -> str:
        return f"user:{user_id}:posts"

    def _key_popular(self) -> str:
        return "posts:popular"

    async def get_or_set_post(self, post_id: int, loader):
        return await self.cache.get_or_set(
            key=self._key_post(post_id), callback=loader, ttl=settings.CACHE_TTL_POST
        )

    async def get_or_set_user_post(self, user_id: int, post_id: int, loader):
        return await self.cache.get_or_set(
            key=self._key_user_post(user_id, post_id),
            callback=loader,
            ttl=settings.CACHE_TTL_POST,
        )

    async def get_or_set_user_posts(self, user_id: int, loader):
        return await self.cache.get_or_set(
            key=self._key_user_posts(user_id),
            callback=loader,
            ttl=settings.CACHE_TTL_USER_POSTS,
        )


    async def invalidate_user_posts(self, user_id: int):
        await self.cache.delete(self._key_user_posts(user_id))


    async def invalidate_post(self, post_id: int, user_id: int):
        await self.cache.delete(self._key_post(post_id))
        await self.cache.delete(self._key_user_post(user_id, post_id))
        await self.invalidate_user_posts(user_id)

