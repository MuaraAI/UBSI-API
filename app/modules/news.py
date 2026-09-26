import asyncio
import json
import re
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status
from scrapling.fetchers import Fetcher

from app.config import settings
from app.envelope import success_response, error_response
from app.cache import cache

router = APIRouter(prefix="/v1/news", tags=["news"])

def clean_html_text(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = text.replace("&#8217;", "'").replace("&#8211;", "-").replace("&amp;", "&").replace("&quot;", '"')
    return " ".join(text.split()).strip()

def parse_wp_posts(raw_posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for p in raw_posts:
        p_id = str(p.get("id", ""))
        title = clean_html_text(p.get("title", {}).get("rendered", ""))
        link = p.get("link", "")
        date = p.get("date", "")
        
        embedded = p.get("_embedded", {})
        authors = embedded.get("author", [])
        author = authors[0].get("name", "Redaksi") if authors else "Redaksi"
        
        media = embedded.get("wp:featuredmedia", [])
        featured_image = media[0].get("source_url") if media else None
        
        excerpt = clean_html_text(p.get("excerpt", {}).get("rendered", ""))

        results.append({
            "id": p_id,
            "title": title,
            "date": date,
            "link": link,
            "author": author,
            "featured_image": featured_image,
            "excerpt": excerpt,
        })
    return results

def parse_wp_post_detail(p: dict[str, Any]) -> dict[str, Any]:
    p_id = str(p.get("id", ""))
    title = clean_html_text(p.get("title", {}).get("rendered", ""))
    link = p.get("link", "")
    date = p.get("date", "")
    
    embedded = p.get("_embedded", {})
    authors = embedded.get("author", [])
    author = authors[0].get("name", "Redaksi") if authors else "Redaksi"
    
    media = embedded.get("wp:featuredmedia", [])
    featured_image = media[0].get("source_url") if media else None
    
    content = p.get("content", {}).get("rendered", "")
    excerpt = clean_html_text(p.get("excerpt", {}).get("rendered", ""))

    return {
        "id": p_id,
        "title": title,
        "date": date,
        "link": link,
        "author": author,
        "featured_image": featured_image,
        "excerpt": excerpt,
        "content": content,
    }

class NewsClient:
    BASE_URL = "https://news.bsi.ac.id/wp-json/wp/v2"

    def fetch_posts(self, search: Optional[str] = None, page: int = 1, per_page: int = 10) -> list[dict[str, Any]]:
        params = f"_embed=1&page={page}&per_page={per_page}"
        if search:
            params += f"&search={search}"
        url = f"{self.BASE_URL}/posts?{params}"

        try:
            res = Fetcher.get(url, timeout=20, impersonate="chrome")
            if res.status == 200:
                raw = res.text if hasattr(res, "text") else res.body.decode("utf-8", "ignore")
                return json.loads(raw)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(
                    code="UPSTREAM_ERROR",
                    message=f"WordPress REST API mengembalikan status {res.status}",
                    module="news"
                )
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="news")
            )

    def fetch_post_detail(self, post_id: str) -> dict[str, Any]:
        url = f"{self.BASE_URL}/posts/{post_id}?_embed=1"
        try:
            res = Fetcher.get(url, timeout=20, impersonate="chrome")
            if res.status == 200:
                raw = res.text if hasattr(res, "text") else res.body.decode("utf-8", "ignore")
                return json.loads(raw)
            if res.status == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_response(code="NOT_FOUND", message="Berita tidak ditemukan", module="news")
                )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=f"Status {res.status}", module="news")
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="news")
            )

news_client = NewsClient()

@router.get("")
async def get_news(
    search: Optional[str] = Query(default=None, description="Kata kunci pencarian berita"),
    page: int = Query(default=1, ge=1, description="Nomor halaman"),
    per_page: int = Query(default=10, ge=1, le=50, description="Jumlah item per halaman")
):
    cache_key = cache.make_key("news", "posts", search=search, page=page, per_page=per_page)

    fresh = await cache.get_fresh(cache_key)
    if fresh is not None:
        return success_response(data=fresh, cached=True)

    async with cache.get_lock(cache_key):
        fresh = await cache.get_fresh(cache_key)
        if fresh is not None:
            return success_response(data=fresh, cached=True)

        try:
            loop = asyncio.get_running_loop()
            raw_data = await loop.run_in_executor(
                None,
                news_client.fetch_posts,
                search,
                page,
                per_page
            )
            data = parse_wp_posts(raw_data)
            await cache.set(cache_key, data, ttl=settings.TTL_NEWS)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="news")
            )

@router.get("/{post_id}")
async def get_news_detail(post_id: str):
    cache_key = cache.make_key("news", "detail", post_id=post_id)

    fresh = await cache.get_fresh(cache_key)
    if fresh is not None:
        return success_response(data=fresh, cached=True)

    async with cache.get_lock(cache_key):
        fresh = await cache.get_fresh(cache_key)
        if fresh is not None:
            return success_response(data=fresh, cached=True)

        try:
            loop = asyncio.get_running_loop()
            raw_data = await loop.run_in_executor(
                None,
                news_client.fetch_post_detail,
                post_id
            )
            data = parse_wp_post_detail(raw_data)
            await cache.set(cache_key, data, ttl=settings.TTL_NEWS)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="news")
            )
