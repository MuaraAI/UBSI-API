import pytest
from httpx import AsyncClient
from app.config import settings

_original_init = AsyncClient.__init__

def _patched_init(self, *args, **kwargs):
    headers = kwargs.get("headers")
    if headers is None:
        headers = {}
    else:
        headers = dict(headers)
    skip = headers.pop("_skip_auto_auth", None)
    if not skip and "X-API-Key" not in headers:
        headers["X-API-Key"] = "test-secret-key-12345"
    kwargs["headers"] = headers
    _original_init(self, *args, **kwargs)

@pytest.fixture(autouse=True)
def auto_auth_client(monkeypatch):
    monkeypatch.setattr(AsyncClient, "__init__", _patched_init)
    monkeypatch.setattr(settings, "API_KEY", "test-secret-key-12345")
