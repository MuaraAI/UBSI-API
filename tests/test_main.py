import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint_redis_up():
    from app.main import cache
    cache._client = None
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["redis"] == "up"
    cache._client = None

@pytest.mark.asyncio
async def test_health_endpoint_redis_down():
    from app.main import cache
    cache._client = None
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = ConnectionError("Redis down")
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["redis"] == "down"
    cache._client = None

@pytest.mark.asyncio
async def test_rate_limiter_middleware_blocks_on_exceeded():
    mock_redis = AsyncMock()
    # Simulate rate limit exceeded (61)
    mock_redis.incr.return_value = 61
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/some-endpoint")
        assert res.status_code == 429
        data = res.json()
        assert data["success"] is False
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

@pytest.mark.asyncio
async def test_modular_creds_validation():
    from app.deps import require_studentv2_creds, require_elearning_creds
    from fastapi import HTTPException
    from app.config import Settings

    empty_settings = Settings(_env_file=None, STUDENTV2_NIM="", STUDENTV2_PASS="")
    with pytest.raises(HTTPException) as exc_info:
        require_studentv2_creds(empty_settings)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["code"] == "CONFIG_MISSING"
    assert exc_info.value.detail["error"]["module"] == "studentv2"

    with pytest.raises(HTTPException) as exc_info:
        require_elearning_creds(empty_settings)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["code"] == "CONFIG_MISSING"
    assert exc_info.value.detail["error"]["module"] == "elearning"
