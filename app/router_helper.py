"""Helper generik untuk pola cache-then-upstream yang dipakai semua router.

Menghapus duplikasi blok 30 baris (fresh check, single-flight lock,
fetch, parse, LGG fallback) yang sebelumnya disalin di setiap endpoint.
Sekaligus menerapkan stale-while-revalidate: data LGG dikirim instan
dengan flag stale sementara refresh upstream berjalan sebagai background
task.
"""
import asyncio
from typing import Any, Callable, Optional

from fastapi import HTTPException, status

from app.cache import cache
from app.envelope import error_response, success_response


async def cached_endpoint(
    module: str,
    name: str,
    fetch: Callable[[], Any],
    parse: Callable[[Any], Any],
    ttl: int,
    cache_params: Optional[dict] = None,
    swr: bool = True,
):
    """Pola standar endpoint: cek cache, fetch upstream dengan lock, fallback LGG.

    - fresh cache -> dikirim dengan cached=True
    - LGG tersedia -> dikirim instan dengan stale=True, refresh di background
      (hanya jika swr=True; kalau False, LGG dikirim tanpa revalidasi)
    - kosong semuanya -> fetch upstream di bawah single-flight lock,
      hasil diparse lalu disimpan dengan TTL
    """
    params = cache_params or {}
    cache_key = cache.make_key(module, name, **params)

    cached = await cache.fresh_or_stale(cache_key)
    if cached is not None:
        data, is_stale = cached
        if is_stale:
            if swr:
                _schedule_revalidate(cache_key, fetch, parse, ttl)
            return success_response(data=data, cached=True, stale=True)
        return success_response(data=data, cached=True)

    async with cache.get_lock(cache_key):
        cached = await cache.fresh_or_stale(cache_key)
        if cached is not None:
            data, is_stale = cached
            if is_stale:
                return success_response(data=data, cached=True, stale=True)
            return success_response(data=data, cached=True)

        try:
            html = fetch()
            if asyncio.iscoroutine(html):
                html = await html
            data = parse(html)
            await cache.set(cache_key, data, ttl=ttl)
            return success_response(data=data, cached=False)
        except Exception as e:
            lgg_result = await cache.get_lgg(cache_key)
            if lgg_result:
                lgg_data, _ = lgg_result
                return success_response(data=lgg_data, cached=True, stale=True)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module=module)
            )


def _schedule_revalidate(
    cache_key: str,
    fetch: Callable[[], Any],
    parse: Callable[[Any], Any],
    ttl: int,
) -> None:
    async def _revalidate():
        try:
            html = fetch()
            if asyncio.iscoroutine(html):
                html = await html
            data = parse(html)
            await cache.set(cache_key, data, ttl=ttl)
        except Exception:
            pass  # background refresh: biarkan LGG tetap terpakai

    try:
        asyncio.create_task(_revalidate())
    except RuntimeError:
        pass  # tidak ada event loop (mis. saat test sinkron) — aman diabaikan
