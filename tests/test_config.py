import pytest
from app.config import Settings

def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("STUDENTV2_NIM", raising=False)
    monkeypatch.delenv("STUDENTV2_PASS", raising=False)
    monkeypatch.delenv("ELEARNING_NIM", raising=False)
    monkeypatch.delenv("ELEARNING_PASS", raising=False)
    
    s = Settings(_env_file=None)
    assert s.HOST == "127.0.0.1"
    assert s.PORT == 8300
    assert s.REDIS_URL == "redis://127.0.0.1:6379/2"
    assert s.TTL_DEFAULT == 60
    assert s.TTL_SCHEDULE == 7200
    assert s.TTL_GRADES == 1800
    assert s.TTL_ASSIGNMENTS == 600
    assert s.TTL_NEWS == 900
    assert s.TTL_LIBRARY == 3600

def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/5")
    monkeypatch.setenv("STUDENTV2_NIM", "15260767")
    monkeypatch.setenv("STUDENTV2_PASS", "secretpass")
    
    s = Settings(_env_file=None)
    assert s.PORT == 9000
    assert s.HOST == "0.0.0.0"
    assert s.REDIS_URL == "redis://localhost:6379/5"
    assert s.STUDENTV2_NIM == "15260767"
    assert s.STUDENTV2_PASS == "secretpass"

def test_security_config_defaults(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("TRUSTED_PROXIES", raising=False)
    cfg = Settings(_env_file=None)
    assert cfg.API_KEY == ""
    assert cfg.ALLOWED_ORIGINS == "*"
    assert cfg.TRUSTED_PROXIES == "127.0.0.1"

def test_vault_and_root_path_settings(monkeypatch):
    monkeypatch.delenv("ROOT_PATH", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    monkeypatch.delenv("VAULT_ENCRYPTION_KEY", raising=False)

    s = Settings(_env_file=None)
    assert s.ROOT_PATH == ""
    assert s.SUPABASE_URL == ""
    assert s.SUPABASE_SERVICE_KEY == ""
    assert s.VAULT_ENCRYPTION_KEY == ""

    s_custom = Settings(
        _env_file=None,
        ROOT_PATH="/v1/ubsi-api",
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_SERVICE_KEY="service_key_test",
        VAULT_ENCRYPTION_KEY="01234567890123456789012345678901",
    )
    assert s_custom.ROOT_PATH == "/v1/ubsi-api"
    assert s_custom.SUPABASE_URL == "https://example.supabase.co"
    assert s_custom.SUPABASE_SERVICE_KEY == "service_key_test"
    assert s_custom.VAULT_ENCRYPTION_KEY == "01234567890123456789012345678901"

