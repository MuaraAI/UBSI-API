import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.config import settings

@pytest.mark.asyncio
async def test_verify_requires_master_key():
    """Member Key cannot access verify endpoint; returns 403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_secret"), \
             patch("app.vault.resolve_member_key", new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = {"nim": "15260767", "elearning_pass": "p1", "studentv2_pass": "p2"}
            res = await ac.post(
                "/v1/auth/verify",
                headers={"X-API-Key": "muara_live_member_key"},
                json={"nim": "15260767", "elearning_pass": "p1", "studentv2_pass": "p2"}
            )
            assert res.status_code == 403
            assert res.json()["error"]["code"] == "FORBIDDEN"

@pytest.mark.asyncio
async def test_verify_without_key_returns_401():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"_skip_auto_auth": "1"}) as ac:
        res = await ac.post(
            "/v1/auth/verify",
            json={"nim": "15260767", "elearning_pass": "p1", "studentv2_pass": "p2"}
        )
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_verify_success_both_services():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_secret"), \
             patch("app.modules.auth.studentv2_client.login", return_value=True), \
             patch("app.modules.auth.elearning_client.login", return_value=True):
            
            res = await ac.post(
                "/v1/auth/verify",
                headers={"X-API-Key": "master_secret"},
                json={"nim": "15260767", "elearning_pass": "pass_el", "studentv2_pass": "pass_sv"}
            )
            assert res.status_code == 200
            data = res.json()["data"]
            assert data["valid"] is True
            assert data["nim"] == "15260767"
            assert data["elearning"]["valid"] is True
            assert data["studentv2"]["valid"] is True

@pytest.mark.asyncio
async def test_verify_partial_failure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_secret"), \
             patch("app.modules.auth.studentv2_client.login", return_value=True), \
             patch("app.modules.auth.elearning_client.login", return_value=False):
            
            res = await ac.post(
                "/v1/auth/verify",
                headers={"X-API-Key": "master_secret"},
                json={"nim": "15260767", "elearning_pass": "wrong_el", "studentv2_pass": "pass_sv"}
            )
            assert res.status_code == 200
            data = res.json()["data"]
            assert data["valid"] is False
            assert data["elearning"]["valid"] is False
            assert data["studentv2"]["valid"] is True

@pytest.mark.asyncio
async def test_verify_rate_limit_per_nim_exceeded():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_secret"), \
             patch("app.modules.auth.limiter.is_allowed", new_callable=AsyncMock) as mock_limiter:
            mock_limiter.return_value = False
            
            res = await ac.post(
                "/v1/auth/verify",
                headers={"X-API-Key": "master_secret"},
                json={"nim": "15260767", "elearning_pass": "p1", "studentv2_pass": "p2"}
            )
            assert res.status_code == 429
            assert res.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
