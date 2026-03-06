import pytest
from unittest.mock import AsyncMock
from src.services.cache.posts_cache import PostsCacheService
from src.config import settings

@pytest.mark.asyncio
async def test_key_post_and_user_post():
    """Проверяем правильность формирования ключей"""
    posts_cache = PostsCacheService(cache=AsyncMock())

    assert posts_cache._key_post(1) == "post:1"
    assert posts_cache._key_user_post(42, 7) == "post:7:user:42"

@pytest.mark.asyncio
async def test_get_or_set_post_calls_cache_correctly():
    """Проверяем, что get_or_set_post вызывает cache.get_or_set с правильными аргументами"""
    mock_cache = AsyncMock()
    mock_cache.get_or_set.return_value = {"id": 1, "title": "Test Post"}

    posts_cache = PostsCacheService(mock_cache)

    async def loader():
        return {"id": 1, "title": "Test Post"}

    result = await posts_cache.get_or_set_post(post_id=1, loader=loader)

    assert result == {"id": 1, "title": "Test Post"}
    mock_cache.get_or_set.assert_awaited_once_with(
        key="post:1",
        callback=loader,
        ttl=settings.CACHE_TTL_POST
    )

@pytest.mark.asyncio
async def test_get_or_set_user_post_calls_cache_correctly():
    """Проверяем, что get_or_set_user_post вызывает cache.get_or_set с правильными аргументами"""
    mock_cache = AsyncMock()
    mock_cache.get_or_set.return_value = {"id": 1, "title": "User Post", "user_id": 42}

    posts_cache = PostsCacheService(mock_cache)

    async def loader():
        return {"id": 1, "title": "User Post", "user_id": 42}

    result = await posts_cache.get_or_set_user_post(user_id=42, post_id=1, loader=loader)

    assert result == {"id": 1, "title": "User Post", "user_id": 42}
    mock_cache.get_or_set.assert_awaited_once_with(
        key="post:1:user:42",
        callback=loader,
        ttl=settings.CACHE_TTL_POST
    )