import pytest
from unittest.mock import MagicMock
from app.main import extract_client_ip

def test_extract_client_ip_cloudflare():
    req = MagicMock()
    req.headers = {"cf-connecting-ip": "203.0.113.195", "x-forwarded-for": "10.0.0.1"}
    req.client.host = "127.0.0.1"
    assert extract_client_ip(req) == "203.0.113.195"

def test_extract_client_ip_x_forwarded_for():
    req = MagicMock()
    req.headers = {"x-forwarded-for": "198.51.100.42, 10.0.0.1"}
    req.client.host = "127.0.0.1"
    assert extract_client_ip(req) == "198.51.100.42"

def test_extract_client_ip_fallback():
    req = MagicMock()
    req.headers = {}
    req.client.host = "127.0.0.1"
    assert extract_client_ip(req) == "127.0.0.1"

def test_extract_client_ip_none_client():
    req = MagicMock()
    req.headers = {}
    req.client = None
    assert extract_client_ip(req) == "127.0.0.1"
