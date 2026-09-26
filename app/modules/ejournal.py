import asyncio
import re
from typing import Any

from fastapi import APIRouter, HTTPException, status
from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptor

from app.config import settings
from app.envelope import success_response, error_response
from app.cache import cache

router = APIRouter(prefix="/v1/ejournal", tags=["ejournal"])

def parse_journal_catalog(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    journals = []
    seen_slugs = set()

    for a in page.css('a[href*="/ejurnal/index.php/"]'):
        href = a.attrib.get("href", "").strip()
        title = " ".join(a.text.split()).strip()
        m = re.search(r"/ejurnal/index.php/([^/#\?]+)/?", href)
        if m:
            slug = m.group(1).lower()
            if slug not in seen_slugs and slug not in ("index", "about", "search"):
                seen_slugs.add(slug)
                display_name = title if title and len(title) > 2 else f"Jurnal {slug.capitalize()}"
                journals.append({
                    "name": display_name,
                    "slug": slug,
                    "url": href if href.startswith("http") else f"https://ejournal.bsi.ac.id{href}",
                })

    return journals

class EJournalClient:
    BASE_URL = "https://ejournal.bsi.ac.id"

    def fetch_catalog(self) -> str:
        # Bypasses Cloudflare challenge via OAI identifier fallback
        url = f"{self.BASE_URL}/ejurnal/oai?verb=Identify"
        try:
            res = Fetcher.get(url, timeout=30, impersonate="chrome")
            if res.status == 200:
                return res.text if hasattr(res, "text") else res.body.decode("utf-8", "ignore")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=f"Status {res.status}", module="ejournal")
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="ejournal")
            )

ejournal_client = EJournalClient()

@router.get("/journals")
async def get_journals():
    cache_key = cache.make_key("ejournal", "catalog")

    fresh = await cache.get_fresh(cache_key)
    if fresh is not None:
        return success_response(data=fresh, cached=True)

    async with cache.get_lock(cache_key):
        fresh = await cache.get_fresh(cache_key)
        if fresh is not None:
            return success_response(data=fresh, cached=True)

        try:
            loop = asyncio.get_running_loop()
            html = await loop.run_in_executor(None, ejournal_client.fetch_catalog)
            data = parse_journal_catalog(html)
            await cache.set(cache_key, data, ttl=settings.TTL_LIBRARY)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="ejournal")
            )
