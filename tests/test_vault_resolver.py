import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.vault import resolve_member_key, encrypt_credential

@pytest.mark.asyncio
async def test_resolve_member_key_cache_miss_fetches_supabase():
    enc_key = "a" * 64
    enc_el = encrypt_credential("mypassword_el", enc_key)
    enc_sv = encrypt_credential("mypassword_sv", enc_key)
    
    mock_db_row = [{
        "nim": "15260767",
        "encrypted_elearning_pass": enc_el,
        "encrypted_studentv2_pass": enc_sv,
        "is_active": True
    }]
    
    with patch("app.vault.settings") as mock_settings, \
         patch("app.vault.cache.get_fresh", new_callable=AsyncMock) as mock_get_cache, \
         patch("app.vault.cache.set", new_callable=AsyncMock) as mock_set_cache, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_http_get:
        
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_KEY = "service_role_secret"
        mock_settings.VAULT_ENCRYPTION_KEY = enc_key
        
        mock_get_cache.return_value = None
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_db_row
        mock_http_get.return_value = mock_resp
        
        res = await resolve_member_key("muara_live_testkey123")
        assert res is not None
        assert res["nim"] == "15260767"
        assert res["elearning_pass"] == "mypassword_el"
        assert res["studentv2_pass"] == "mypassword_sv"
        assert mock_set_cache.called

@pytest.mark.asyncio
async def test_resolve_member_key_cache_hit_skips_supabase():
    cached_payload = {
        "nim": "15260767",
        "elearning_pass": "cached_pass",
        "studentv2_pass": "cached_pass"
    }
    with patch("app.vault.settings") as mock_settings, \
         patch("app.vault.cache.get_fresh", new_callable=AsyncMock) as mock_get_cache, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_http_get:
        
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_KEY = "service_role_secret"
        mock_settings.VAULT_ENCRYPTION_KEY = "a" * 64
        
        mock_get_cache.return_value = cached_payload
        
        res = await resolve_member_key("muara_live_cachedkey")
        assert res == cached_payload
        assert not mock_http_get.called

@pytest.mark.asyncio
async def test_resolve_member_key_unconfigured_returns_none():
    with patch("app.vault.settings") as mock_settings:
        mock_settings.SUPABASE_URL = ""
        mock_settings.SUPABASE_SERVICE_KEY = ""
        mock_settings.VAULT_ENCRYPTION_KEY = ""
        
        res = await resolve_member_key("muara_live_anykey")
        assert res is None

@pytest.mark.asyncio
async def test_resolve_member_key_not_found_returns_none():
    with patch("app.vault.settings") as mock_settings, \
         patch("app.vault.cache.get_fresh", new_callable=AsyncMock) as mock_get_cache, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_http_get:
        
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_KEY = "service_role_secret"
        mock_settings.VAULT_ENCRYPTION_KEY = "a" * 64
        
        mock_get_cache.return_value = None
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_http_get.return_value = mock_resp
        
        res = await resolve_member_key("muara_live_unknownkey")
        assert res is None

@pytest.mark.asyncio
async def test_resolve_member_key_network_error_returns_none():
    with patch("app.vault.settings") as mock_settings, \
         patch("app.vault.cache.get_fresh", new_callable=AsyncMock) as mock_get_cache, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_http_get:
        
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_KEY = "service_role_secret"
        mock_settings.VAULT_ENCRYPTION_KEY = "a" * 64
        
        mock_get_cache.return_value = None
        mock_http_get.side_effect = Exception("Connection timed out")
        
        res = await resolve_member_key("muara_live_failingkey")
        assert res is None
