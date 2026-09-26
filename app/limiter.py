from datetime import datetime
from typing import Optional
import redis.asyncio as aioredis

class RateLimiter:
    def __init__(self, redis_url: str, limit: int = 60):
        self.redis_url = redis_url
        self.limit = limit
        self._client: Optional[aioredis.Redis] = None

    async def get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def is_allowed(self, client_id: str) -> bool:
        try:
            client = await self.get_client()
            minute_bucket = datetime.now().strftime("%Y%m%d%H%M")
            key = f"ubsi:ratelimit:{client_id}:{minute_bucket}"
            count = await client.incr(key)
            if count == 1:
                await client.expire(key, 65)
            return count <= self.limit
        except (aioredis.RedisError, ConnectionError, OSError):
            return True
