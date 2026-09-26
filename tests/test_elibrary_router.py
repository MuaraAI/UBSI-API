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
async def test_search_books_endpoint():
    mock_html = (FIXTURES / "el_search_ok.html").read_text(encoding="utf-8")
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.elibrary.elibrary_client.fetch_search", return_value=mock_html):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/elibrary/search?q=metode&opsi=buku")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["data"]["total_count"] == 967
        assert len(data["data"]["items"]) >= 10

@pytest.mark.asyncio
async def test_book_detail_endpoint():
    mock_html = (FIXTURES / "el_book_detail.html").read_text(encoding="utf-8")
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.elibrary.elibrary_client.fetch_book", return_value=mock_html):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/elibrary/book/206060")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["data"]["kode_buku"] == "206060"
        assert data["data"]["penulis"] == "Sugiyono"
        assert data["data"]["stok"] == 3
