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
async def test_full_pipeline_integration(monkeypatch):
    monkeypatch.setenv("STUDENTV2_NIM", "15260767")
    monkeypatch.setenv("STUDENTV2_PASS", "secret")
    monkeypatch.setenv("ELEARNING_NIM", "15260767")
    monkeypatch.setenv("ELEARNING_PASS", "secret")

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    sv2_html = (FIXTURES / "sv2_jadwal.html").read_text(encoding="utf-8")
    el_html = (FIXTURES / "el_sch.html").read_text(encoding="utf-8")
    lib_html = (FIXTURES / "el_search_ok.html").read_text(encoding="utf-8")
    repo_html = """<div class="ep_view_blurb"><a href="/100">Sistem AI</a></div>"""
    ej_html = """<a href="/ejurnal/index.php/wanastra/">Wanastra</a>"""
    wp_news = [{"id": 1, "date": "2026-09-25", "title": {"rendered": "Berita"}, "link": "http://link", "excerpt": {"rendered": "..."}}]

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.studentv2.studentv2_client.fetch_page", return_value=sv2_html), \
         patch("app.modules.elearning.elearning_client.fetch_page", return_value=el_html), \
         patch("app.modules.elibrary.elibrary_client.fetch_search", return_value=lib_html), \
         patch("app.modules.repository.repository_client.fetch_recent", return_value=repo_html), \
         patch("app.modules.ejournal.ejournal_client.fetch_catalog", return_value=ej_html), \
         patch("app.modules.news.news_client.fetch_posts", return_value=wp_news):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1. Health
            r_health = await ac.get("/health")
            assert r_health.status_code == 200
            assert r_health.json()["status"] == "ok"

            # 2. News
            r_news = await ac.get("/v1/news")
            assert r_news.status_code == 200
            assert r_news.json()["success"] is True

            # 3. Elibrary
            r_lib = await ac.get("/v1/elibrary/search?q=algoritma")
            assert r_lib.status_code == 200
            assert r_lib.json()["success"] is True

            # 4. Repository
            r_repo = await ac.get("/v1/repository/recent")
            assert r_repo.status_code == 200
            assert r_repo.json()["success"] is True

            # 5. EJournal
            r_ej = await ac.get("/v1/ejournal/journals")
            assert r_ej.status_code == 200
            assert r_ej.json()["success"] is True

            # 6. StudentV2
            r_sv2 = await ac.get("/v1/studentv2/schedule")
            assert r_sv2.status_code == 200
            assert r_sv2.json()["success"] is True
            assert len(r_sv2.json()["data"]) == 6

            # 7. Elearning
            r_el = await ac.get("/v1/elearning/courses")
            assert r_el.status_code == 200
            assert r_el.json()["success"] is True
            assert len(r_el.json()["data"]) == 6
