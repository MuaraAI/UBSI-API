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
