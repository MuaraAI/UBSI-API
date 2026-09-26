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
async def test_get_courses_success(monkeypatch):
    monkeypatch.setenv("ELEARNING_NIM", "15260767")
    monkeypatch.setenv("ELEARNING_PASS", "secret")

    mock_html = (FIXTURES / "el_sch.html").read_text(encoding="utf-8")
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.elearning.elearning_client.fetch_page", return_value=mock_html):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/elearning/courses")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["data"]) == 6
        assert data["data"][0]["kode"] == "101"
        assert data["data"][0]["token_absen"] is not None

@pytest.mark.asyncio
async def test_get_assignments_with_token(monkeypatch):
    monkeypatch.setenv("ELEARNING_NIM", "15260767")
    monkeypatch.setenv("ELEARNING_PASS", "secret")

    mock_html = (FIXTURES / "el_assignment_1.html").read_text(encoding="utf-8")
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis), \
         patch("app.modules.elearning.elearning_client.fetch_page", return_value=mock_html):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/v1/elearning/assignments?token=custom_token")

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "tasks" in data["data"]
        assert "submissions" in data["data"]

@pytest.mark.asyncio
async def test_get_presence_and_materials_and_quiz(monkeypatch):
    monkeypatch.setenv("ELEARNING_NIM", "15260767")
    monkeypatch.setenv("ELEARNING_PASS", "secret")

    mock_absen_html = (FIXTURES / "el_absen_1.html").read_text(encoding="utf-8")
    mock_learning_html = (FIXTURES / "el_learning_1.html").read_text(encoding="utf-8")
    mock_quiz_html = (FIXTURES / "el_exercise.html").read_text(encoding="utf-8")

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.incr.return_value = 1

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        with patch("app.modules.elearning.elearning_client.fetch_page", return_value=mock_absen_html):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                res_p = await ac.get("/v1/elearning/presence?token=test_tok")
            assert res_p.status_code == 200
            assert res_p.json()["success"] is True

        with patch("app.modules.elearning.elearning_client.fetch_page", return_value=mock_learning_html):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                res_m = await ac.get("/v1/elearning/materials?token=test_tok")
            assert res_m.status_code == 200
            assert res_m.json()["success"] is True

        with patch("app.modules.elearning.elearning_client.fetch_page", return_value=mock_quiz_html):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                res_q = await ac.get("/v1/elearning/quiz")
            assert res_q.status_code == 200
            assert res_q.json()["success"] is True
