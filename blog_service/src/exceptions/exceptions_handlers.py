from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.exceptions.exceptions import BlogException


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(BlogException)
    async def blog_exception_handler(request: Request, exc: BlogException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
