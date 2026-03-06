from typing import Dict, List, Optional

from src.exceptions.exceptions import (
    PostNotFoundException,
    PostAlreadyExistException,
    UserNotFoundException,
    PermissionErrorException,
    ObjectNotFoundException,
)
from src.schemas.posts_schemas import PostOUT, PostEdit, PostAdd, PostCreateRequest
from src.services.base import BaseService
from src.services.cache.cache_service import BaseCacheService
from src.services.cache.posts_cache import PostsCacheService


class PostsService(BaseService):
    def __init__(self, db, cache: Optional[BaseCacheService] = None):
        super().__init__(db, cache)
        self.post_cache = PostsCacheService(cache) if cache else None

    async def get_all_posts(self, skip: int = 0, limit: int = 20) -> List[PostOUT]:
        posts = await self.db.posts.get_filtered(skip=skip, limit=limit)
        return [PostOUT.model_validate(p) for p in posts]

    async def get_user_posts(self, user_id: int) -> List[PostOUT]:
        if not self.post_cache:
            posts = await self.db.posts.get_filtered(user_id=user_id)
            return [PostOUT.model_validate(p) for p in posts]

        async def load_user_posts():
            posts = await self.db.posts.get_filtered(user_id=user_id)
            return [PostOUT.model_validate(post).model_dump() for post in posts]

        posts_data = await self.post_cache.get_or_set_user_posts(
            user_id, load_user_posts
        )
        sorted_data = sorted(posts_data, key=lambda x: x["id"])
        return [PostOUT(**data) for data in sorted_data]

    async def get_user_post_by_id(self, user_id: int, post_id: int) -> PostOUT:
        if not self.post_cache:
            try:
                post = await self.db.posts.get_one(id=post_id, user_id=user_id)
                return PostOUT.model_validate(post)
            except ObjectNotFoundException:
                raise PostNotFoundException()

        async def load_user_post():
            try:
                post = await self.db.posts.get_one(id=post_id, user_id=user_id)
                return PostOUT.model_validate(post).model_dump()
            except ObjectNotFoundException:
                raise PostNotFoundException()

        data = await self.post_cache.get_or_set_user_post(
            user_id, post_id, load_user_post
        )
        return PostOUT(**data)

    async def add_post(self, user_id: int, data: PostCreateRequest) -> PostOUT:
        if not await self.db.users.exists(id=user_id):
            raise UserNotFoundException

        existing = await self.db.posts.exists(user_id=user_id, title=data.title)
        if existing:
            raise PostAlreadyExistException()

        add_stmt = PostAdd(user_id=user_id, title=data.title, content=data.content)
        post = await self.db.posts.add(add_stmt)
        await self.db.commit()

        if self.post_cache:
            print(f"🔄 Cache exists, invalidating for user {user_id}")
            await self.post_cache.invalidate_user_posts(user_id)
            print(f"✅ Invalidation called")


        return PostOUT.model_validate(post)

    async def partially_edit_post(
        self, post_id: int, user_id: int, data: PostEdit
    ) -> PostOUT:
        post = await self.db.posts.get_one_or_none(id=post_id)
        if not post:
            raise PostNotFoundException()
        if post.user_id != user_id:
            raise PermissionErrorException()

        edited_post = await self.db.posts.edit(data, id=post_id, exclude_unset=True)
        await self.db.commit()

        if self.post_cache:
            await self.post_cache.invalidate_post(post_id, user_id)

        return PostOUT.model_validate(edited_post)

    async def delete_post(self, user_id: int, post_id: int) -> Dict:
        post = await self.db.posts.get_one_or_none(id=post_id)
        if not post:
            raise PostNotFoundException()
        if post.user_id != user_id:
            raise PermissionErrorException()

        await self.db.posts.delete(id=post_id)
        await self.db.commit()

        if self.post_cache:
            await self.post_cache.invalidate_post(post_id, user_id)

        return {"status": "ok", "message": f"Пост {post_id} удален"}
