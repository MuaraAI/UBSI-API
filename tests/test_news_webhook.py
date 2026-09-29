import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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
    monkeypatch.setattr(settings, "DISCORD_WEBHOOK_URL", "")
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "")
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
         patch("app.modules.news.broadcast_news_article") as mock_broadcast:
        
        count = await poll_news_webhook()
        assert count == 0
        mock_broadcast.assert_not_called()
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
    mock_redis.sismember.side_effect = lambda key, val: val == "102"
    
    with patch("app.cache.cache.get_client", return_value=mock_redis), \
         patch("app.modules.news.news_client.fetch_posts", return_value=mock_posts), \
         patch("app.modules.news.broadcast_news_article", return_value={"custom": True}) as mock_broadcast:
        
        count = await poll_news_webhook()
        assert count == 1
        assert mock_broadcast.call_count == 1
        dispatched_data = mock_broadcast.call_args[0][0]
        assert dispatched_data["id"] == "103"
        assert dispatched_data["title"] == "Berita Baru 3"
        mock_redis.sadd.assert_called_with("ubsi:news:seen_ids", "103")

@pytest.mark.asyncio
async def test_dispatch_discord_webhook():
    from app.modules.news import dispatch_discord_webhook
    sample_post = {
        "id": "1",
        "title": "Judul Discord",
        "link": "https://news.bsi.ac.id/test",
        "excerpt": "Cuplikan singkat",
        "author": "Penulis",
        "featured_image": "https://news.bsi.ac.id/img.jpg"
    }
    
    mock_res = MagicMock()
    mock_res.is_success = True
    
    with patch("httpx.AsyncClient.post", return_value=mock_res) as mock_post:
        ok = await dispatch_discord_webhook(sample_post, "https://discord.com/api/webhooks/123/abc")
        assert ok is True
        assert mock_post.call_count == 1
        payload = mock_post.call_args[1]["json"]
        assert "embeds" in payload
        assert payload["embeds"][0]["title"] == "Judul Discord"
        assert payload["embeds"][0]["color"] == 0x2DD4BF
        assert payload["embeds"][0]["image"]["url"] == "https://news.bsi.ac.id/img.jpg"

@pytest.mark.asyncio
async def test_dispatch_telegram_message():
    from app.modules.news import dispatch_telegram_message
    sample_post = {
        "id": "2",
        "title": "Judul Telegram",
        "link": "https://news.bsi.ac.id/test",
        "excerpt": "Cuplikan singkat telegram",
        "author": "Penulis",
        "date": "2026-09-29",
        "featured_image": "https://news.bsi.ac.id/img.jpg"
    }
    
    mock_res = MagicMock()
    mock_res.is_success = True
    
    with patch("httpx.AsyncClient.post", return_value=mock_res) as mock_post:
        ok = await dispatch_telegram_message(sample_post, "bot123456", "@testchannel")
        assert ok is True
        assert mock_post.call_count == 1
        url = mock_post.call_args[0][0]
        assert "sendPhoto" in url
        payload = mock_post.call_args[1]["json"]
        assert payload["chat_id"] == "@testchannel"
        assert "Judul Telegram" in payload["caption"]

@pytest.mark.asyncio
async def test_broadcast_news_article_multi_channel(monkeypatch):
    monkeypatch.setattr(settings, "DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/mock")
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "mock_token")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "-100123")
    monkeypatch.setattr(settings, "NEWS_WEBHOOK_URL", "https://custom.hook/api")
    from app.modules.news import broadcast_news_article
    
    sample_post = {"id": "1", "title": "Test Multi"}
    with patch("app.modules.news.dispatch_discord_webhook", return_value=True) as mock_dc, \
         patch("app.modules.news.dispatch_telegram_message", return_value=True) as mock_tg, \
         patch("app.modules.news.dispatch_webhook_notification", return_value=True) as mock_custom:
        
        results = await broadcast_news_article(sample_post)
        assert results == {"discord": True, "telegram": True, "custom": True}
        assert mock_dc.call_count == 1
        assert mock_tg.call_count == 1
        assert mock_custom.call_count == 1

@pytest.mark.asyncio
async def test_news_webhook_test_endpoint_channels(monkeypatch):
    monkeypatch.setattr(settings, "DISCORD_WEBHOOK_URL", "https://discord.test")
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "mock_token")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "-100123")
    monkeypatch.setattr(settings, "NEWS_WEBHOOK_URL", "https://custom.test")
    
    with patch("app.modules.news.dispatch_discord_webhook", return_value=True), \
         patch("app.modules.news.dispatch_telegram_message", return_value=True), \
         patch("app.modules.news.dispatch_webhook_notification", return_value=True):
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/v1/news/webhook/test?channel=all")
            
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        results = data["data"]["results"]
        assert results["discord"]["success"] is True
        assert results["telegram"]["success"] is True
        assert results["custom"]["success"] is True
