import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.cache import cache
from app.limiter import limiter

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def reset_clients():
    cache._client = None
    limiter._client = None
    yield
    cache._client = None
    limiter._client = None


@pytest.mark.asyncio
async def test_dashboard_menggabungkan_empat_seksi(monkeypatch):
    monkeypatch.setenv("STUDENTV2_NIM", "15260225")
    monkeypatch.setenv("STUDENTV2_PASS", "secret")

    jadwal = (FIXTURES / "sv2_jadwal.html").read_text(encoding="utf-8")
    nilai = (FIXTURES / "sv2_nilai_murni.html").read_text(encoding="utf-8")
    berita = (FIXTURES / "sv2_berita.html").read_text(encoding="utf-8")

    def fake_fetch(path, nim, password):
        if "jadwal" in path:
            return jadwal
        if "nilai" in path:
            return nilai
        if "berita" in path:
            return berita
        return berita

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.studentv2.studentv2_client.fetch_page", side_effect=fake_fetch):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/studentv2/dashboard")

    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    # Empat seksi harus lengkap
    assert set(data.keys()) == {"schedule", "grades", "news", "announcements"}


@pytest.mark.asyncio
async def test_dashboard_tetap_sukses_saat_satu_seksi_gagal(monkeypatch):
    monkeypatch.setenv("STUDENTV2_NIM", "15260225")
    monkeypatch.setenv("STUDENTV2_PASS", "secret")

    jadwal = (FIXTURES / "sv2_jadwal.html").read_text(encoding="utf-8")

    def fake_fetch(path, nim, password):
        if "jadwal" in path:
            return jadwal
        raise RuntimeError("upstream down")

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.studentv2.studentv2_client.fetch_page", side_effect=fake_fetch):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/studentv2/dashboard")

    # Satu seksi gagal tidak meruntuhkan seluruh dashboard
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "schedule" in body["data"]
    assert body["data"]["schedule"] is not None
