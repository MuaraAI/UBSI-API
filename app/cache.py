import asyncio
from datetime import datetime, timezone, timedelta
import hashlib
import json
from typing import Any, Optional
import redis.asyncio as aioredis

WIB = timezone(timedelta(hours=7))

class CacheManager:
    def __init__(self, redis_url: str, default_ttl: int = 60):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._client: Optional[aioredis.Redis] = None
        self._locks: dict[str, asyncio.Lock] = {}

    async def get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    def make_key(self, module: str, path: str, **params: Any) -> str:
        param_str = json.dumps(params, sort_keys=True)
        h = hashlib.sha256(f"{module}:{path}:{param_str}".encode()).hexdigest()[:16]
        return f"ubsi:{module}:{h}"

    async def get_fresh(self, key: str) -> Optional[Any]:
        try:
            client = await self.get_client()
            raw = await client.get(f"{key}:fresh")
            return json.loads(raw) if raw else None
        except (aioredis.RedisError, ConnectionError, OSError):
            return None

    async def get_lgg(self, key: str) -> Optional[tuple[Any, str]]:
        try:
            client = await self.get_client()
            raw = await client.get(f"{key}:lgg")
            if not raw:
                return None
            data = json.loads(raw)
            stale_since = data.get("_saved_at", "unknown")
            return data.get("payload"), stale_since
        except (aioredis.RedisError, ConnectionError, OSError):
            return None

    async def set(self, key: str, payload: Any, ttl: Optional[int] = None) -> None:
        try:
            client = await self.get_client()
            effective_ttl = ttl if ttl is not None else self.default_ttl
            now_str = datetime.now(WIB).isoformat()
            body = json.dumps(payload)
            lgg_body = json.dumps({
                "payload": payload,
                "_saved_at": now_str
            })
            await client.set(f"{key}:fresh", body, ex=effective_ttl)
            await client.set(f"{key}:lgg", lgg_body)
        except (aioredis.RedisError, ConnectionError, OSError):
            pass

    def get_lock(self, key: str) -> asyncio.Lock:
        """In-process single-flight lock per key to prevent concurrent upstream hits."""
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def fresh_or_stale(self, key: str) -> Optional[tuple[Any, bool]]:
        """Ambil data fresh; kalau kosong, ambil LGG sebagai cadangan.

        Return (data, is_stale) atau None kalau dua-duanya kosong.
        Dipakai router untuk pola stale-while-revalidate: data LGG dikirim
        instan dengan flag stale, refresh upstream berjalan di belakang.
        """
        fresh = await self.get_fresh(key)
        if fresh is not None:
            return fresh, False
        lgg = await self.get_lgg(key)
        if lgg:
            return lgg[0], True
        return None

from app.config import settings
cache = CacheManager(settings.REDIS_URL, default_ttl=settings.TTL_DEFAULT)
