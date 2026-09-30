"""Per-NIM session pool agar request antar user tidak saling menimpa sesi."""
import asyncio
import time
from typing import Any


class SessionPool:
    """Pool sesi login per-NIM dengan TTL idle.

    Sebelumnya satu singleton session dipakai semua request: kalau dua NIM
    berbeda memanggil bersamaan, request kedua memakai sesi NIM pertama
    sehingga data bisa salah orang. Pool ini menyimpan satu client per NIM
    dan menutup sesi yang idle melewati TTL.
    """

    def __init__(self, factory, ttl_seconds: int = 900):
        self._factory = factory
        self._ttl = ttl_seconds
        self._sessions: dict[str, tuple[Any, float]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, nim: str) -> asyncio.Lock:
        if nim not in self._locks:
            self._locks[nim] = asyncio.Lock()
        return self._locks[nim]

    def get(self, nim: str) -> Any:
        entry = self._sessions.get(nim)
        if entry is None:
            try:
                client = self._factory(nim)
            except TypeError:
                client = self._factory()
            self._sessions[nim] = (client, time.monotonic())
            return client
        client, _ = entry
        # Perpanjang TTL tiap kali dipakai
        self._sessions[nim] = (client, time.monotonic())
        return client

    async def evict_idle(self) -> int:
        """Tutup sesi yang idle melewati TTL. Return jumlah sesi yang ditutup."""
        now = time.monotonic()
        stale = [nim for nim, (_, last_used) in self._sessions.items() if now - last_used > self._ttl]
        closed = 0
        for nim in stale:
            entry = self._sessions.pop(nim, None)
            if entry:
                client, _ = entry
                try:
                    close = getattr(client, "close", None)
                    if close:
                        result = close()
                        if asyncio.iscoroutine(result):
                            await result
                except Exception:
                    pass
                closed += 1
        return closed

    def invalidate(self, nim: str) -> None:
        """Tutup dan buang sesi satu NIM (mis. login expired)."""
        entry = self._sessions.pop(nim, None)
        if entry:
            client, _ = entry
            try:
                close = getattr(client, "close", None)
                if close:
                    close()
            except Exception:
                pass

    def __len__(self) -> int:
        return len(self._sessions)
