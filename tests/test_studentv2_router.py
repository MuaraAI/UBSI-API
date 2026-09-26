import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
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
async def test_get_schedule_cached_and_fresh(monkeypatch):
    monkeypatch.setenv("STUDENTV2_NIM", "15260767")
    monkeypatch.setenv("STUDENTV2_PASS", "secret")
    
    mock_html = (FIXTURES / "sv2_jadwal.html").read_text(encoding="utf-8")
    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # miss
    mock_redis.incr.return_value = 1
    
    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.studentv2.studentv2_client.fetch_page", return_value=mock_html):
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/studentv2/schedule")
        
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["cached"] is False
        assert len(data["data"]) == 6
        assert data["data"][0]["kode"] != ""

@pytest.mark.asyncio
async def test_get_grades_success(monkeypatch):
    monkeypatch.setenv("STUDENTV2_NIM", "15260767")
    monkeypatch.setenv("STUDENTV2_PASS", "secret")
    
    mock_html = (FIXTURES / "sv2_nilai_murni.html").read_text(encoding="utf-8")
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1
    
    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.studentv2.studentv2_client.fetch_page", return_value=mock_html):
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/studentv2/grades")
        
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) == 6

@pytest.mark.asyncio
async def test_get_news_and_announcements(monkeypatch):
    monkeypatch.setenv("STUDENTV2_NIM", "15260767")
    monkeypatch.setenv("STUDENTV2_PASS", "secret")
    
    mock_news_html = (FIXTURES / "sv2_berita.html").read_text(encoding="utf-8")
    mock_ann_html = (FIXTURES / "sv2_beranda.html").read_text(encoding="utf-8")
    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1
    
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        with patch("app.modules.studentv2.studentv2_client.fetch_page", return_value=mock_news_html):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                res_news = await ac.get("/v1/studentv2/news?limit=10")
            assert res_news.status_code == 200
            assert len(res_news.json()["data"]) == 10

        with patch("app.modules.studentv2.studentv2_client.fetch_page", return_value=mock_ann_html):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                res_ann = await ac.get("/v1/studentv2/announcements")
            assert res_ann.status_code == 200
            assert len(res_ann.json()["data"]) >= 1

@pytest.mark.asyncio
async def test_studentv2_lgg_fallback_on_upstream_error(monkeypatch):
    monkeypatch.setenv("STUDENTV2_NIM", "15260767")
    monkeypatch.setenv("STUDENTV2_PASS", "secret")

    import json
    stale_payload = {
        "payload": [{"kode": "101", "nama": "PENDIDIKAN PANCASILA"}],
        "_saved_at": "2026-09-26T08:00:00"
    }

    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 1
    # fresh is None, lgg is stale_payload
    async def mock_get(key):
        if ":fresh" in key:
            return None
        if ":lgg" in key:
            return json.dumps(stale_payload)
        return None

    mock_redis.get.side_effect = mock_get

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.studentv2.studentv2_client.fetch_page", side_effect=Exception("BSI server down")):
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/studentv2/schedule")
        
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["cached"] is True
        assert data["stale"] is True
        assert data["data"][0]["kode"] == "101"
