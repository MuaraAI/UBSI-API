from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.cache import cache
from app.limiter import limiter
from app.envelope import error_response
from app.modules.studentv2 import router as studentv2_router, studentv2_client
from app.modules.elearning import router as elearning_router, elearning_client
from app.modules.elibrary import router as elibrary_router
from app.modules.news import router as news_router
from app.modules.repository import router as repository_router
from app.modules.ejournal import router as ejournal_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    try:
        studentv2_client.close()
        elearning_client.close()
        client = await cache.get_client()
        await client.aclose()
    except Exception:
        pass

app = FastAPI(
    title="UBSI API",
    description="Private Unofficial API Aggregator for UBSI Services",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(studentv2_router)
app.include_router(elearning_router)
app.include_router(elibrary_router)
app.include_router(news_router)
app.include_router(repository_router)
app.include_router(ejournal_router)

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    path = request.url.path
    # Skip rate limiting for health check and OpenAPI docs
    if path in ("/health", "/docs", "/openapi.json", "/redoc"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "127.0.0.1"
    is_allowed = await limiter.is_allowed(client_ip)
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response(
                code="RATE_LIMIT_EXCEEDED",
                message="Rate limit exceeded (max 60 req/min)"
            )
        )
    return await call_next(request)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code="HTTP_ERROR", message=str(exc.detail))
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(code="INTERNAL_SERVER_ERROR", message=str(exc))
    )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    redis_status = "down"
    try:
        client = await cache.get_client()
        pong = await client.ping()
        if pong:
            redis_status = "up"
    except Exception:
        redis_status = "down"
    return {"status": "ok", "redis": redis_status}
