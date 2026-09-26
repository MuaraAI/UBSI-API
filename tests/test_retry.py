import pytest
from app.retry import retry_async


@pytest.mark.asyncio
async def test_sukses_pada_percobaan_pertama():
    calls = []

    def fn():
        calls.append(1)
        return "ok"

    result = await retry_async(fn, attempts=3)
    assert result == "ok"
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_retry_sampai_sukses(monkeypatch):
    async def no_sleep(delay):
        return None

    monkeypatch.setattr("app.retry.asyncio.sleep", no_sleep)
    monkeypatch.setattr("app.retry.random.uniform", lambda a, b: a)
    calls = []

    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("blip")
        return "akhirnya"

    result = await retry_async(fn, attempts=5, base_delay=0.01)
    assert result == "akhirnya"
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_gagal_semua_percobaan(monkeypatch):
    async def no_sleep(delay):
        return None

    monkeypatch.setattr("app.retry.asyncio.sleep", no_sleep)
    monkeypatch.setattr("app.retry.random.uniform", lambda a, b: a)
    calls = []

    def fn():
        calls.append(1)
        raise ValueError("selalu gagal")

    with pytest.raises(ValueError):
        await retry_async(fn, attempts=3, base_delay=0.01)
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_mendukung_fn_async():
    async def fn():
        return "async ok"

    result = await retry_async(fn, attempts=2)
    assert result == "async ok"
