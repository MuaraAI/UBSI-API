import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings

@pytest.mark.asyncio
async def test_health_check_bypasses_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"_skip_auto_auth": "1"}) as ac:
        res = await ac.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_cors_options_preflight_bypasses_auth():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={
            "_skip_auto_auth": "1",
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    ) as ac:
        res = await ac.options("/v1/news")
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers

@pytest.mark.asyncio
async def test_missing_api_key_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"_skip_auto_auth": "1"}) as ac:
        res = await ac.get("/v1/news")
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["module"] == "auth"

@pytest.mark.asyncio
async def test_invalid_api_key_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"X-API-Key": "wrong-key"}) as ac:
        res = await ac.get("/v1/news")
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_valid_api_key_allows_request():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"X-API-Key": "test-secret-key-12345"}) as ac:
        res = await ac.get("/health")
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_metrics_requires_api_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"_skip_auto_auth": "1"}) as ac:
        res = await ac.get("/metrics")
    assert res.status_code == 401
