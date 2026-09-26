import os
import secrets
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.cache import cache
from app.limiter import limiter
from app.envelope import error_response
from app.modules.studentv2 import router as studentv2_router, studentv2_client
from app.modules.elearning import router as elearning_router, pooled_elearning_client
from app.modules.elibrary import router as elibrary_router
from app.modules.news import router as news_router
from app.modules.repository import router as repository_router
from app.modules.ejournal import router as ejournal_router

def extract_client_ip(request: Request) -> str:
    """Ekstraksi IP klien dengan prioritas Cloudflare -> Forwarded Proxy -> socket host."""
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not settings.API_KEY and not os.getenv("PYTEST_CURRENT_TEST"):
        raise RuntimeError("API_KEY wajib disetel di file .env!")
    yield
    try:
        studentv2_client.close()
        pooled_elearning_client.close()
        client = await cache.get_client()
        await client.aclose()
    except Exception:
        pass

app = FastAPI(
    title="UBSI API",
    description="Private Unofficial API Aggregator for UBSI Services",
    version="1.1.0",
    lifespan=lifespan
)

app.include_router(studentv2_router)
app.include_router(elearning_router)
app.include_router(elibrary_router)
app.include_router(news_router)
app.include_router(repository_router)
app.include_router(ejournal_router)

@app.middleware("http")
async def api_key_auth_middleware(request: Request, call_next):
    # 1. Allow OPTIONS (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)

    # 2. Allow /health without auth
    if request.url.path == "/health":
        return await call_next(request)

    # 3. Validate X-API-Key
    api_key = request.headers.get("x-api-key")
    configured_key = settings.API_KEY

    if not api_key or not configured_key or not secrets.compare_digest(api_key, configured_key):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                code="UNAUTHORIZED",
                message="Akses ditolak: Header X-API-Key tidak valid atau tidak disertakan",
                module="auth"
            )
        )

    return await call_next(request)

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    path = request.url.path
    # Skip rate limiting for health check and OpenAPI docs
    if path in ("/health", "/docs", "/openapi.json", "/redoc"):
        return await call_next(request)

    client_ip = extract_client_ip(request)
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

# CORS Middleware added after HTTP middlewares so it wraps outermost
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
if not origins or "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        content=error_response(code="INTERNAL_SERVER_ERROR", message="Terjadi kesalahan internal pada server")
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


@app.get("/metrics", status_code=status.HTTP_200_OK)
async def metrics():
    """Ringkasan kesehatan scraper: ukuran pool sesi dan status Redis."""
    sv2_pool = getattr(studentv2_client, "_pool", None)
    sv2_sessions = len(sv2_pool) if sv2_pool is not None else 0
    el_pool = getattr(pooled_elearning_client, "_pool", None)
    el_sessions = len(el_pool) if el_pool is not None else 0

    redis_status = "down"
    try:
        client = await cache.get_client()
        pong = await client.ping()
        if pong:
            redis_status = "up"
    except Exception:
        redis_status = "down"
    return {
        "status": "ok",
        "redis": redis_status,
        "active_sessions": sv2_sessions + el_sessions,
        "studentv2_sessions": sv2_sessions,
        "elearning_sessions": el_sessions,
        "uptime_note": "sessions are per-NIM with 15 min idle TTL",
    }
