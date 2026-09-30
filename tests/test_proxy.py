import pytest
from app.proxy import normalize_proxy, get_proxy
from app.config import settings

def test_normalize_proxy_formats():
    # 1. Already has protocol
    assert normalize_proxy("http://103.1.2.3:8080") == "http://103.1.2.3:8080"
    assert normalize_proxy("socks5://103.1.2.3:1080") == "socks5://103.1.2.3:1080"
    
    # 2. Bare IP:Port
    assert normalize_proxy("103.1.2.3:8080") == "http://103.1.2.3:8080"
    
    # 3. IP:Port:User:Pass format
    assert normalize_proxy("103.1.2.3:8080:user1:pass1") == "http://user1:pass1@103.1.2.3:8080"
    
    # 4. User:Pass@IP:Port format
    assert normalize_proxy("user1:pass1@103.1.2.3:8080") == "http://user1:pass1@103.1.2.3:8080"
    
    # 5. Empty or whitespace
    assert normalize_proxy("") is None
    assert normalize_proxy("   ") is None

def test_get_proxy_unconfigured(monkeypatch):
    monkeypatch.setattr(settings, "SCRAPER_PROXY", "")
    monkeypatch.setattr(settings, "SCRAPER_PROXY_POOL", "")
    assert get_proxy() is None
    assert get_proxy(seed="15260767") is None

def test_get_proxy_single_proxy(monkeypatch):
    monkeypatch.setattr(settings, "SCRAPER_PROXY", "103.5.6.7:8080")
    monkeypatch.setattr(settings, "SCRAPER_PROXY_POOL", "")
    assert get_proxy() == "http://103.5.6.7:8080"
    assert get_proxy(seed="15260767") == "http://103.5.6.7:8080"

def test_get_proxy_pool_random_and_sticky(monkeypatch):
    pool_str = "10.0.0.1:8080, 10.0.0.2:8080, socks5://10.0.0.3:1080"
    monkeypatch.setattr(settings, "SCRAPER_PROXY", "")
    monkeypatch.setattr(settings, "SCRAPER_PROXY_POOL", pool_str)
    
    expected = [
        "http://10.0.0.1:8080",
        "http://10.0.0.2:8080",
        "socks5://10.0.0.3:1080"
    ]
    
    # Random selection
    chosen = get_proxy()
    assert chosen in expected
    
    # Sticky seed: same NIM always yields same proxy
    nim_a = "15260767"
    proxy_a_1 = get_proxy(seed=nim_a)
    proxy_a_2 = get_proxy(seed=nim_a)
    assert proxy_a_1 == proxy_a_2
    assert proxy_a_1 in expected

def test_client_receives_proxy():
    from app.modules.studentv2 import StudentV2Client
    from app.modules.elearning import ElearningClient

    c_sv = StudentV2Client(proxy="http://103.1.2.3:8080")
    assert c_sv._proxy == "http://103.1.2.3:8080"
    
    c_el = ElearningClient(proxy="http://103.1.2.3:8080")
    assert c_el._proxy == "http://103.1.2.3:8080"

