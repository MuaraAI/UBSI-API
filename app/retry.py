"""Retry dengan exponential backoff dan jitter untuk panggilan upstream."""
import asyncio
import random
from typing import Any, Callable


async def retry_async(
    fn: Callable[[], Any],
    attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 8.0,
):
    """Jalankan fn (sync atau async) hingga attempts kali dengan backoff eksponensial.

    Delay antar percobaan: base_delay * 2^i dengan jitter acak (0.5x-1.5x),
    dibatasi max_delay. Exception terakhir dilempar kembali jika semua gagal.
    """
    last_error: Exception | None = None
    for i in range(attempts):
        try:
            result = fn()
            if asyncio.iscoroutine(result):
                return await result
            return result
        except Exception as exc:  # noqa: BLE001 - dilempar ulang setelah batas
            last_error = exc
            if i < attempts - 1:
                delay = min(max_delay, base_delay * (2 ** i))
                jitter = delay * random.uniform(0.5, 1.5)
                await asyncio.sleep(jitter)
    assert last_error is not None
    raise last_error
