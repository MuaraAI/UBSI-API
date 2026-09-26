import pytest
from unittest.mock import AsyncMock, patch
from app.limiter import RateLimiter

@pytest.mark.asyncio
async def test_rate_limiter_within_limit():
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 1
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        limiter = RateLimiter("redis://127.0.0.1:6379/2", limit=60)
        allowed = await limiter.is_allowed("127.0.0.1")
        assert allowed is True
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()

@pytest.mark.asyncio
async def test_rate_limiter_exceeded():
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 61
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        limiter = RateLimiter("redis://127.0.0.1:6379/2", limit=60)
        allowed = await limiter.is_allowed("127.0.0.1")
        assert allowed is False
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_not_called()
