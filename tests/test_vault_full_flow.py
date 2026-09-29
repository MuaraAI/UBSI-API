import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.config import settings
from app.vault import encrypt_credential

@pytest.mark.asyncio
async def test_full_flow_master_key_standalone():
    """Master Key standalone: passes auth, unmetered rate limits."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "API_KEY", "master_key_standalone"):
            res = await ac.get("/v1/news", headers={"X-API-Key": "master_key_standalone"})
            assert res.status_code == 200
            assert res.json()["success"] is True

@pytest.mark.asyncio
async def test_full_flow_member_key_vault_resolution():
    """Member Key in cloud mode: decodes credentials and injects into request."""
    enc_key = "f" * 64
    el_pass = "el_secret_pass_123"
    sv_pass = "sv_secret_pass_456"
    
    enc_el = encrypt_credential(el_pass, enc_key)
    enc_sv = encrypt_credential(sv_pass, enc_key)
    
    mock_row = [{
        "nim": "15260767",
        "encrypted_elearning_pass": enc_el,
        "encrypted_studentv2_pass": enc_sv,
        "is_active": True
    }]
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value=mock_row)
    
    mock_supabase_client = AsyncMock()
    mock_supabase_client.__aenter__.return_value = mock_supabase_client
    mock_supabase_client.get = AsyncMock(return_value=mock_resp)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "SUPABASE_URL", "https://example.supabase.co"), \
             patch.object(settings, "SUPABASE_SERVICE_KEY", "serv_key"), \
             patch.object(settings, "VAULT_ENCRYPTION_KEY", enc_key), \
             patch("app.vault.cache.get_fresh", new_callable=AsyncMock) as mock_cache_get, \
             patch("app.vault.cache.set", new_callable=AsyncMock) as mock_cache_set, \
             patch("app.vault.httpx.AsyncClient", return_value=mock_supabase_client):
            
            mock_cache_get.return_value = None
            
            # Request to public endpoint with member key
            res = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_full_test"})
            assert res.status_code == 200
            assert res.json()["success"] is True
            assert mock_supabase_client.get.called
            assert mock_cache_set.called

@pytest.mark.asyncio
async def test_full_flow_invalid_member_key_rejected():
    """Member key that does not exist or is inactive returns 401."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value=[])
    
    mock_supabase_client = AsyncMock()
    mock_supabase_client.__aenter__.return_value = mock_supabase_client
    mock_supabase_client.get = AsyncMock(return_value=mock_resp)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch.object(settings, "SUPABASE_URL", "https://example.supabase.co"), \
             patch.object(settings, "SUPABASE_SERVICE_KEY", "serv_key"), \
             patch.object(settings, "VAULT_ENCRYPTION_KEY", "f" * 64), \
             patch("app.vault.cache.get_fresh", new_callable=AsyncMock) as mock_cache_get, \
             patch("app.vault.httpx.AsyncClient", return_value=mock_supabase_client):
            
            mock_cache_get.return_value = None
            
            res = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_revoked"})
            assert res.status_code == 401
            assert res.json()["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_full_flow_rate_limit_per_member_key_isolation():
    """Rate limit applies to member key, distinct from other keys."""
    transport = ASGITransport(app=app)
    
    mock_member = {
        "nim": "15260767",
        "elearning_pass": "pwd1",
        "studentv2_pass": "pwd2"
    }
    
    with patch("app.vault.resolve_member_key", new_callable=AsyncMock) as mock_resolve, \
         patch("app.main.limiter.is_allowed", new_callable=AsyncMock) as mock_limiter:
        mock_resolve.return_value = mock_member
        
        # Key A allowed
        mock_limiter.return_value = True
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r1 = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_key_a"})
            assert r1.status_code == 200
            
        # Key B rate limit exceeded
        mock_limiter.return_value = False
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r2 = await ac.get("/v1/news", headers={"X-API-Key": "muara_live_key_b"})
            assert r2.status_code == 429
            assert r2.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
