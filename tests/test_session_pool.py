import pytest
from app.session_pool import SessionPool


class FakeClient:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_pool_menorehkan_satu_client_per_nim():
    pool = SessionPool(FakeClient, ttl_seconds=60)
    a = pool.get("111")
    b = pool.get("111")
    c = pool.get("222")
    assert a is b, "NIM sama harus memakai client yang sama"
    assert a is not c, "NIM beda harus client berbeda"
    assert len(pool) == 2


@pytest.mark.asyncio
async def test_evict_idle_menutup_sesi_kadaluarsa():
    pool = SessionPool(FakeClient, ttl_seconds=-1)
    client = pool.get("111")
    closed = await pool.evict_idle()
    assert closed == 1
    assert client.closed is True
    assert len(pool) == 0


def test_invalidate_menutup_sesi_nim_tertentu():
    pool = SessionPool(FakeClient, ttl_seconds=60)
    a = pool.get("111")
    pool.invalidate("111")
    assert a.closed is True
    assert len(pool) == 0
    # get berikutnya membuat client baru
    b = pool.get("111")
    assert b is not a
