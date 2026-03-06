import os
from zoneinfo import ZoneInfo

from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):

    MODE: str

    REDIS_CACHE_HOST: str
    REDIS_CACHE_PORT: int
    REDIS_CACHE_PASS: str

    REDIS_CACHE_DEFAULT_TTL: int
    CACHE_TTL_POST: int
    CACHE_TTL_USER_POSTS: int

    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    TIME_ZONE: str

    @property
    def REDIS_CACHE_URL(self) -> str:
        return f"redis://:{self.REDIS_CACHE_PASS}@{self.REDIS_CACHE_HOST}:{self.REDIS_CACHE_PORT}/0"

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TZ(self):
        return ZoneInfo(self.TIME_ZONE)

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", "../.secrets/.env"),
        env_file_encoding="utf-8",
    )


settings = Settings()  # type: ignore
