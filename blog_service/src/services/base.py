from src.services.cache.cache_service import BaseCacheService
from src.utils.db_manager import DBManager


class BaseService:
    def __init__(self, db: DBManager, cache: BaseCacheService | None = None):
        self.db = db
        self.cache = cache
