import asyncio
import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Path, Query, status
from scrapling.fetchers import Fetcher

from app.config import settings
from app.envelope import success_response, error_response
from app.cache import cache
from app.router_helper import cached_endpoint

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
            safe_search = urllib.parse.quote_plus(search)
            params += f"&search={safe_search}"
        url = f"{self.BASE_URL}/posts?{params}"

        try:
            res = Fetcher.get(url, timeout=20, impersonate="chrome")
            if res.status == 200:
                if hasattr(res, "json") and callable(res.json):
                    return res.json()
                raw = res.body.decode("utf-8", "ignore") if isinstance(res.body, bytes) else str(res.body)
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
                if hasattr(res, "json") and callable(res.json):
                    return res.json()
                raw = res.body.decode("utf-8", "ignore") if isinstance(res.body, bytes) else str(res.body)
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
    loop = asyncio.get_running_loop()
    return await cached_endpoint(
        module="news",
        name="posts",
        fetch=lambda: loop.run_in_executor(None, news_client.fetch_posts, search, page, per_page),
        parse=parse_wp_posts,
        ttl=settings.TTL_NEWS,
        cache_params={"search": search, "page": page, "per_page": per_page},
    )

@router.get("/{post_id}")
async def get_news_detail(post_id: str = Path(..., pattern=r"^[0-9]+$")):
    loop = asyncio.get_running_loop()
    return await cached_endpoint(
        module="news",
        name="detail",
        fetch=lambda: loop.run_in_executor(None, news_client.fetch_post_detail, post_id),
        parse=parse_wp_post_detail,
        ttl=settings.TTL_NEWS,
        cache_params={"post_id": post_id},
    )

# ============================================================================
# News Webhook Auto-Notification
# ============================================================================

async def dispatch_webhook_notification(post: dict[str, Any], webhook_url: str) -> bool:
    payload = {
        "event": "news.published",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": post,
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.post(webhook_url, json=payload)
            return res.is_success
    except Exception:
        return False

async def poll_news_webhook() -> int:
    """Cek artikel berita baru dan dispatch ke webhook jika ada.

    Mengembalikan jumlah notifikasi yang berhasil dikirim.
    """
    if not settings.NEWS_WEBHOOK_URL:
        return 0

    redis = await cache.get_client()
    key_seen = "ubsi:news:seen_ids"

    loop = asyncio.get_running_loop()
    try:
        raw_posts = await loop.run_in_executor(None, news_client.fetch_posts, None, 1, 5)
        posts = parse_wp_posts(raw_posts)
    except Exception:
        return 0

    if not posts:
        return 0

    # Cold start: seed IDs tanpa mengirim spam
    exists = await redis.exists(key_seen)
    if not exists:
        ids = [p["id"] for p in posts if p.get("id")]
        if ids:
            await redis.sadd(key_seen, *ids)
            await redis.expire(key_seen, 86400 * 30)
        return 0

    dispatched_count = 0
    for p in reversed(posts):
        p_id = p.get("id")
        if not p_id:
            continue
        is_member = await redis.sismember(key_seen, p_id)
        if not is_member:
            ok = await dispatch_webhook_notification(p, settings.NEWS_WEBHOOK_URL)
            if ok:
                await redis.sadd(key_seen, p_id)
                dispatched_count += 1

    return dispatched_count

async def news_webhook_worker():
    while True:
        try:
            await poll_news_webhook()
        except Exception:
            pass
        await asyncio.sleep(settings.NEWS_WEBHOOK_INTERVAL)

@router.post("/webhook/test")
async def test_news_webhook(target_url: Optional[str] = Query(default=None, description="URL target alternatif")):
    """Kirim payload uji coba ke webhook untuk memverifikasi endpoint consumer."""
    webhook_url = target_url or settings.NEWS_WEBHOOK_URL
    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                code="CONFIG_MISSING",
                message="NEWS_WEBHOOK_URL belum disetel di .env atau parameter target_url kosong",
                module="news"
            )
        )
    sample_post = {
        "id": "test_99999",
        "title": "Uji Coba Notifikasi Webhook Berita UBSI",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "link": "https://news.bsi.ac.id/sample-article",
        "author": "Redaksi UBSI API",
        "featured_image": None,
        "excerpt": "Ini adalah payload contoh verifikasi koneksi webhook dari UBSI API.",
    }
    ok = await dispatch_webhook_notification(sample_post, webhook_url)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(
                code="DELIVERY_FAILED",
                message=f"Gagal mengirim webhook ke {webhook_url}",
                module="news"
            )
        )
    return success_response(data={"message": f"Webhook test berhasil dikirim ke {webhook_url}", "payload": sample_post})
