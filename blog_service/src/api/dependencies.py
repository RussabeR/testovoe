from typing import Annotated

from fastapi import Depends, Header, Request

from src.connectors.database import async_session_maker
from src.connectors.redis_client import RedisManager
from src.services.cache.cache_service import BaseCacheService

from src.utils.db_manager import DBManager


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_redis(request: Request) -> RedisManager:
    return request.app.state.redis


RedisDep = Annotated[RedisManager, Depends(get_redis)]


# Заглушка для авторизации
async def get_current_user_id(
    authorization: str | None = Header(
        None, description="JWT токен (заглушка)", include_in_schema=False
    )
) -> int:

    return 33


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


def get_cache(request: Request) -> BaseCacheService:
    redis: RedisManager = request.app.state.redis
    return BaseCacheService(redis)


CacheDep = Annotated[BaseCacheService, Depends(get_cache)]
