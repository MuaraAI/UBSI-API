import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app
from app.config import settings

@pytest.mark.asyncio
async def test_auth_master_key_allows_request():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_secret_123"):
            res = await ac.get("/v1/news", headers={"X-API-Key": "master_secret_123"})
            assert res.status_code == 200

@pytest.mark.asyncio
async def test_auth_member_key_resolves_and_allows_request():
    transport = ASGITransport(app=app)
    member_payload = {
        "nim": "15260767",
        "elearning_pass": "pwd_el_123",
        "studentv2_pass": "pwd_sv_123",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_secret_123"), \
             patch("app.vault.resolve_member_key", new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = member_payload
            
            res = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_valid123"})
            assert res.status_code == 200
            assert mock_resolve.called

@pytest.mark.asyncio
async def test_auth_member_key_invalid_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_secret_123"), \
             patch("app.vault.resolve_member_key", new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = None
            
            res = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_invalidkey"})
            assert res.status_code == 401
            data = res.json()
            assert data["success"] is False
            assert data["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_auth_empty_or_whitespace_key_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/v1/news", headers={"X-API-Key": "   ", "_skip_auto_auth": "1"})
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_rate_limiter_isolates_member_keys():
    transport = ASGITransport(app=app)
    member_payload = {
        "nim": "15260767",
        "elearning_pass": "pwd1",
        "studentv2_pass": "pwd2",
    }
    with patch("app.vault.resolve_member_key", new_callable=AsyncMock) as mock_resolve, \
         patch("app.main.limiter.is_allowed", new_callable=AsyncMock) as mock_limiter:
        mock_resolve.return_value = member_payload
        
        # Key 1 allowed
        mock_limiter.return_value = True
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r1 = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_key1"})
            assert r1.status_code == 200
        
        # Key 2 blocked by rate limit
        mock_limiter.return_value = False
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r2 = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_key2"})
            assert r2.status_code == 429
            assert r2.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
