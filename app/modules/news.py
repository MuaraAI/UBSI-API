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
# News Multi-Channel Auto-Notification (Discord, Telegram, Custom)
# ============================================================================

async def dispatch_webhook_notification(post: dict[str, Any], webhook_url: str) -> bool:
    """Kirim generic JSON payload ke custom webhook URL."""
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

async def dispatch_discord_webhook(post: dict[str, Any], webhook_url: str) -> bool:
    """Kirim rich embed ke Discord Webhook."""
    embed: dict[str, Any] = {
        "title": post.get("title", "Berita Baru UBSI"),
        "url": post.get("link", ""),
        "description": post.get("excerpt", ""),
        "color": 0x2DD4BF,  # Teal #2DD4BF
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": f"Oleh: {post.get('author', 'Redaksi')} • UBSI News Portal"},
    }
    if post.get("featured_image"):
        embed["image"] = {"url": post["featured_image"]}

    payload = {
        "username": "UBSI News",
        "avatar_url": "https://ubsi-api.muaraai.com/assets/images/brand-logos/logo_bsi.png",
        "embeds": [embed],
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.post(webhook_url, json=payload)
            return res.is_success
    except Exception:
        return False

async def dispatch_telegram_message(post: dict[str, Any], bot_token: str, chat_id: str) -> bool:
    """Kirim pesan HTML dengan foto (jika ada) ke Telegram via Bot API."""
    title = post.get("title", "Berita Kampus UBSI")
    link = post.get("link", "https://news.bsi.ac.id")
    excerpt = post.get("excerpt", "")
    author = post.get("author", "Redaksi")
    date = post.get("date", "")
    image_url = post.get("featured_image")

    caption = (
        f"📰 <b><a href=\"{link}\">{title}</a></b>\n\n"
        f"{excerpt}\n\n"
        f"✍️ <i>{author}</i> • 📅 {date}\n"
        f"🔗 <a href=\"{link}\">Baca Selengkapnya di Portal Berita</a>"
    )

    base_url = f"https://api.telegram.org/bot{bot_token}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if image_url:
                res = await client.post(
                    f"{base_url}/sendPhoto",
                    json={
                        "chat_id": chat_id,
                        "photo": image_url,
                        "caption": caption[:1024],
                        "parse_mode": "HTML",
                    },
                )
                if res.is_success:
                    return True
            # Fallback sendMessage jika tanpa gambar atau sendPhoto gagal
            res2 = await client.post(
                f"{base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": caption[:4096],
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
            )
            return res2.is_success
    except Exception:
        return False

async def broadcast_news_article(post: dict[str, Any]) -> dict[str, bool]:
    """Kirim artikel secara paralel ke seluruh channel yang aktif."""
    tasks: dict[str, Any] = {}
    if settings.DISCORD_WEBHOOK_URL:
        tasks["discord"] = dispatch_discord_webhook(post, settings.DISCORD_WEBHOOK_URL)
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        tasks["telegram"] = dispatch_telegram_message(post, settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
    if settings.NEWS_WEBHOOK_URL:
        tasks["custom"] = dispatch_webhook_notification(post, settings.NEWS_WEBHOOK_URL)

    if not tasks:
        return {}

    keys = list(tasks.keys())
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    return {k: (bool(r) and not isinstance(r, Exception)) for k, r in zip(keys, results)}

async def poll_news_webhook() -> int:
    """Cek artikel berita baru dan broadcast ke seluruh channel aktif."""
    has_channel = bool(
        settings.DISCORD_WEBHOOK_URL
        or (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
        or settings.NEWS_WEBHOOK_URL
    )
    if not has_channel:
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
            results = await broadcast_news_article(p)
            if any(results.values()):
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
async def test_news_webhook(
    channel: str = Query(default="all", pattern=r"^(all|discord|telegram|custom)$", description="Channel target: all, discord, telegram, custom"),
    target_url: Optional[str] = Query(default=None, description="URL target override (khusus custom/discord)")
):
    """Kirim payload uji coba ke Discord, Telegram, atau Custom Webhook."""
    sample_post = {
        "id": "test_99999",
        "title": "Uji Coba Notifikasi Berita Kampus UBSI",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "link": "https://news.bsi.ac.id/sample-article",
        "author": "Redaksi UBSI API",
        "featured_image": "https://news.bsi.ac.id/wp-content/uploads/2026/09/banner.jpg",
        "excerpt": "Ini adalah payload contoh verifikasi koneksi broadcast webhook multi-channel dari UBSI API.",
    }

    results: dict[str, Any] = {}
    if channel in ("all", "discord"):
        discord_url = target_url or settings.DISCORD_WEBHOOK_URL
        if discord_url:
            ok = await dispatch_discord_webhook(sample_post, discord_url)
            results["discord"] = {"configured": True, "success": ok, "target": discord_url}
        else:
            results["discord"] = {"configured": False, "message": "DISCORD_WEBHOOK_URL belum disetel"}

    if channel in ("all", "telegram"):
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
            ok = await dispatch_telegram_message(sample_post, settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
            results["telegram"] = {"configured": True, "success": ok, "chat_id": settings.TELEGRAM_CHAT_ID}
        else:
            results["telegram"] = {"configured": False, "message": "TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID belum disetel"}

    if channel in ("all", "custom"):
        custom_url = target_url or settings.NEWS_WEBHOOK_URL
        if custom_url:
            ok = await dispatch_webhook_notification(sample_post, custom_url)
            results["custom"] = {"configured": True, "success": ok, "target": custom_url}
        else:
            results["custom"] = {"configured": False, "message": "NEWS_WEBHOOK_URL belum disetel"}

    any_configured = any(r.get("configured") for r in results.values())
    if not any_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                code="CONFIG_MISSING",
                message=f"Tidak ada konfigurasi aktif untuk channel '{channel}'. Setel di .env atau kirim parameter target_url.",
                module="news"
            )
        )

    return success_response(data={"message": f"Pengujian broadcast channel '{channel}' selesai", "results": results})
