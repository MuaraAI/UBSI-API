import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
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
async def test_poll_news_webhook_disabled(monkeypatch):
    monkeypatch.setattr(settings, "NEWS_WEBHOOK_URL", "")
    from app.modules.news import poll_news_webhook
    count = await poll_news_webhook()
    assert count == 0

@pytest.mark.asyncio
async def test_poll_news_webhook_cold_start(monkeypatch):
    monkeypatch.setattr(settings, "NEWS_WEBHOOK_URL", "https://mock-webhook.test/news")
    from app.modules.news import poll_news_webhook
    
    mock_posts = [
        {"id": 101, "title": {"rendered": "Berita 1"}, "link": "https://news.bsi.ac.id/1", "date": "2026-09-29"},
        {"id": 102, "title": {"rendered": "Berita 2"}, "link": "https://news.bsi.ac.id/2", "date": "2026-09-29"},
    ]
    
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = 0  # Cold start: key does not exist yet
    
    with patch("app.cache.cache.get_client", return_value=mock_redis), \
         patch("app.modules.news.news_client.fetch_posts", return_value=mock_posts), \
         patch("app.modules.news.dispatch_webhook_notification") as mock_dispatch:
        
        count = await poll_news_webhook()
        assert count == 0
        mock_dispatch.assert_not_called()
        # Verify IDs were seeded into Redis
        mock_redis.sadd.assert_called_once()
        args = mock_redis.sadd.call_args[0]
        assert args[0] == "ubsi:news:seen_ids"
        assert set(args[1:]) == {"101", "102"}

@pytest.mark.asyncio
async def test_poll_news_webhook_dispatches_new_articles(monkeypatch):
    monkeypatch.setattr(settings, "NEWS_WEBHOOK_URL", "https://mock-webhook.test/news")
    from app.modules.news import poll_news_webhook
    
    mock_posts = [
        {"id": 103, "title": {"rendered": "Berita Baru 3"}, "link": "https://news.bsi.ac.id/3", "date": "2026-09-29"},
        {"id": 102, "title": {"rendered": "Berita Lama 2"}, "link": "https://news.bsi.ac.id/2", "date": "2026-09-28"},
    ]
    
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = 1  # Already seeded
    # 102 is seen, 103 is not
    mock_redis.sismember.side_effect = lambda key, val: val == "102"
    
    with patch("app.cache.cache.get_client", return_value=mock_redis), \
         patch("app.modules.news.news_client.fetch_posts", return_value=mock_posts), \
         patch("app.modules.news.dispatch_webhook_notification", return_value=True) as mock_dispatch:
        
        count = await poll_news_webhook()
        assert count == 1
        assert mock_dispatch.call_count == 1
        dispatched_data = mock_dispatch.call_args[0][0]
        assert dispatched_data["id"] == "103"
        assert dispatched_data["title"] == "Berita Baru 3"
        mock_redis.sadd.assert_called_with("ubsi:news:seen_ids", "103")

@pytest.mark.asyncio
async def test_news_webhook_test_endpoint():
    with patch("app.modules.news.dispatch_webhook_notification", return_value=True) as mock_dispatch:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/v1/news/webhook/test?target_url=https://mock.hook/endpoint")
            
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "berhasil" in data["data"]["message"]
        assert mock_dispatch.call_count == 1
