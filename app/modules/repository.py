import asyncio
import hashlib
import re
import urllib.parse
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptor

from app.config import settings
from app.envelope import error_response
from app.router_helper import cached_endpoint
from app.proxy import get_proxy

router = APIRouter(prefix="/v1/repository", tags=["repository"])

def parse_repository_items(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    items = []
    seen_urls = set()

    for el in page.css("div.ep_view_blurb, p.ep_view_blurb, div.ep_search_results"):
        for a in el.css("a"):
            href = a.attrib.get("href", "").strip()
            title = " ".join(a.text.split()).strip()
            if href and title and len(title) > 5 and href not in seen_urls:
                seen_urls.add(href)
                m_id = re.search(r"/(\d+)/?", href)
                item_id = m_id.group(1) if m_id else hashlib.sha256(href.encode()).hexdigest()[:12]
                
                # Check for year in text
                m_year = re.search(r"\((\d{4})\)", el.text)
                year = int(m_year.group(1)) if m_year else None

                items.append({
                    "id": item_id,
                    "title": title,
                    "url": href if href.startswith("http") else f"https://repository.bsi.ac.id{href}",
                    "year": year,
                })

    # Fallback to any content links if ep_view_blurb is absent
    if not items:
        for a in page.css('a[href*="/viewitem/"], a[href*="/view/"], a[href*="/id/eprint/"], a[href*="/repo/"]'):
            href = a.attrib.get("href", "").strip()
            title = " ".join(a.text.split()).strip()
            m_id = re.search(r"/repo/(\d+)/?", href) or re.search(r"/(\d+)/?", href)
            if href and title and len(title) > 5 and href not in seen_urls and m_id:
                seen_urls.add(href)
                item_id = m_id.group(1)
                items.append({
                    "id": item_id,
                    "title": title,
                    "url": href if href.startswith("http") else f"https://repository.bsi.ac.id{href}",
                    "year": None,
                })

    return items

class RepositoryClient:
    BASE_URL = "https://repository.bsi.ac.id"

    def fetch_recent(self) -> str:
        url = f"{self.BASE_URL}/"
        try:
            res = Fetcher.get(url, timeout=30, impersonate="chrome", proxy=get_proxy())
            if res.status == 200:
                body = res.body if isinstance(res.body, bytes) else str(res.body).encode("utf-8")
                return body.decode("utf-8", "ignore")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=f"Status {res.status}", module="repository")
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="repository")
            )

    def fetch_search(self, q: str) -> str:
        safe_q = urllib.parse.quote_plus(q)
        url = f"{self.BASE_URL}/cgi/search/simple?q={safe_q}"
        try:
            res = Fetcher.get(url, timeout=30, impersonate="chrome", proxy=get_proxy())
            if res.status == 200:
                body = res.body if isinstance(res.body, bytes) else str(res.body).encode("utf-8")
                return body.decode("utf-8", "ignore")
            # fallback search path
            fallback_url = f"{self.BASE_URL}/index.php/repo/search?q={safe_q}"
            res_fb = Fetcher.get(fallback_url, timeout=30, impersonate="chrome", proxy=get_proxy())
            if res_fb.status == 200:
                body_fb = res_fb.body if isinstance(res_fb.body, bytes) else str(res_fb.body).encode("utf-8")
                return body_fb.decode("utf-8", "ignore")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message="Repository search error", module="repository")
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="repository")
            )

repository_client = RepositoryClient()

@router.get("/recent")
async def get_recent_repository():
    loop = asyncio.get_running_loop()
    return await cached_endpoint(
        module="repository",
        name="recent",
        fetch=lambda: loop.run_in_executor(None, repository_client.fetch_recent),
        parse=parse_repository_items,
        ttl=settings.TTL_LIBRARY,
    )

@router.get("/search")
async def search_repository(q: str = Query(..., min_length=1, description="Kata kunci pencarian")):
    loop = asyncio.get_running_loop()
    return await cached_endpoint(
        module="repository",
        name="search",
        fetch=lambda: loop.run_in_executor(None, repository_client.fetch_search, q),
        parse=parse_repository_items,
        ttl=settings.TTL_LIBRARY,
        cache_params={"q": q},
    )
