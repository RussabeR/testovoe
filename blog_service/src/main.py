from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
import redis.asyncio as redis
from src.config import settings
from src.connectors.redis_client import RedisManager
from logger import logger
from src.utils.rate_limiter import init_rate_limiter
from src.exceptions.exceptions_handlers import register_exception_handlers
from src.api.api import router as post_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    client = redis.Redis(
        host=settings.REDIS_CACHE_HOST,
        port=settings.REDIS_CACHE_PORT,
        password=settings.REDIS_CACHE_PASS,
        decode_responses=True,
    )

    redis_mgr = RedisManager(client)
    app.state.redis = redis_mgr
    logger.info("Redis connected and stored in app.state")

    yield

    await client.close()
    logger.info("Redis closed")


app = FastAPI(
    lifespan=lifespan,
    title="AtTrainer API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/api",
)

init_rate_limiter(app)
register_exception_handlers(app)
app.include_router(post_router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters=app.swagger_ui_parameters,
    )


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", reload=True, port=8000)
