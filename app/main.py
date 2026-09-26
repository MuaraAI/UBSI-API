from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.cache import CacheManager
from app.limiter import RateLimiter
from app.envelope import error_response

cache = CacheManager(settings.REDIS_URL, default_ttl=settings.TTL_DEFAULT)
limiter = RateLimiter(settings.REDIS_URL, limit=60)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    try:
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
