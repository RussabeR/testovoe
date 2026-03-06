import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.config import settings


class TestLimiter:
    """Заглушка для rate limiter в тестовом режиме"""

    def limit(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


IS_TEST = getattr(settings, "MODE", None) == "TEST" or os.getenv("TEST_MODE") == "true"

if IS_TEST:
    limiter = TestLimiter()

else:
    limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests per minute, try again later"},
    )


def init_rate_limiter(app):

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
