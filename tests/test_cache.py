import pytest
import json
from unittest.mock import AsyncMock, patch
from app.cache import CacheManager

@pytest.mark.asyncio
async def test_cache_make_key():
    cache = CacheManager("redis://127.0.0.1:6379/2")
    k1 = cache.make_key("studentv2", "schedule")
    k2 = cache.make_key("studentv2", "schedule")
    k3 = cache.make_key("studentv2", "schedule", semester="1")
    assert k1 == k2
    assert k1 != k3
    assert k1.startswith("ubsi:studentv2:")

@pytest.mark.asyncio
async def test_cache_set_and_get_fresh():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps({"foo": "bar"})
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        cache = CacheManager("redis://127.0.0.1:6379/2", default_ttl=60)
        
        await cache.set("ubsi:studentv2:123", {"foo": "bar"}, ttl=300)
        assert mock_redis.set.call_count == 2
        
        # Verify fresh call
        mock_redis.set.assert_any_call("ubsi:studentv2:123:fresh", json.dumps({"foo": "bar"}), ex=300)

        # Verify get_fresh
        val = await cache.get_fresh("ubsi:studentv2:123")
        assert val == {"foo": "bar"}

@pytest.mark.asyncio
async def test_cache_get_lgg():
    mock_redis = AsyncMock()
    saved_payload = {"payload": {"foo": "bar"}, "_saved_at": "2026-09-26T10:00:00"}
    mock_redis.get.return_value = json.dumps(saved_payload)
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        cache = CacheManager("redis://127.0.0.1:6379/2")
        data, stale_since = await cache.get_lgg("ubsi:studentv2:123")
        assert data == {"foo": "bar"}
        assert stale_since == "2026-09-26T10:00:00"

@pytest.mark.asyncio
async def test_cache_graceful_on_redis_error():
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = ConnectionError("Redis down")
    mock_redis.set.side_effect = ConnectionError("Redis down")
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        cache = CacheManager("redis://127.0.0.1:6379/2")
        fresh = await cache.get_fresh("any_key")
        assert fresh is None
        lgg = await cache.get_lgg("any_key")
        assert lgg is None
        # set should not raise
        await cache.set("any_key", {"foo": "bar"})


