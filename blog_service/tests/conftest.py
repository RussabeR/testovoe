
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.posts_services import PostsService
from src.services.cache.cache_service import BaseCacheService


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.posts = MagicMock()
    db.users = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def mock_cache():
    return AsyncMock(spec=BaseCacheService)


@pytest.fixture
def posts_service(mock_db, mock_cache):
    return PostsService(mock_db, mock_cache)