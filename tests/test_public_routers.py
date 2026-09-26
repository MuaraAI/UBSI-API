import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.cache import cache
from app.limiter import limiter

@pytest.fixture(autouse=True)
def reset_clients():
    cache._client = None
    limiter._client = None
    yield
    cache._client = None
    limiter._client = None

@pytest.mark.asyncio
async def test_get_news_endpoints():
    mock_posts = [
        {
            "id": 10,
            "date": "2026-09-25T10:00:00",
            "link": "https://news.bsi.ac.id/post-10",
            "title": {"rendered": "Berita Kampus UBSI"},
            "excerpt": {"rendered": "Ringkasan..."},
            "_embedded": {}
        }
    ]
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.news.news_client.fetch_posts", return_value=mock_posts):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/news?page=1&per_page=5")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == "Berita Kampus UBSI"

@pytest.mark.asyncio
async def test_repository_endpoints():
    sample_html = """
    <div class="ep_view_blurb">
      <a href="https://repository.bsi.ac.id/index.php/repo/viewitem/999">Sistem Pakar AI</a> (2026)
    </div>
    """
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.repository.repository_client.fetch_recent", return_value=sample_html):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/repository/recent")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == "Sistem Pakar AI"

@pytest.mark.asyncio
async def test_ejournal_endpoints():
    sample_html = """
    <a href="/ejurnal/index.php/wanastra/">Wanastra</a>
    """
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.ejournal.ejournal_client.fetch_catalog", return_value=sample_html):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/ejournal/journals")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["slug"] == "wanastra"
