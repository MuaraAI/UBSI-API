import asyncio
import re
import time
import urllib.parse
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status
from scrapling.fetchers import Fetcher
from scrapling.parser import Adaptor

from app.config import settings
from app.envelope import success_response, error_response
from app.cache import cache

router = APIRouter(prefix="/v1/elibrary", tags=["elibrary"])

# ============================================================================
# Pure Parsers (Unit-tested against snapshot fixtures)
# ============================================================================

def parse_opac_search(html: str) -> dict[str, Any]:
    page = Adaptor(html)
    full_text = page.get_all_text() if hasattr(page, "get_all_text") else page.text
    
    m_count = re.search(r"Ditemukan\s+(\d+)\s+hasil", full_text)
    total_count = int(m_count.group(1)) if m_count else 0

    seen_urls = set()
    items = []

    for a in page.css('a[href*="readbook"], a[href*="tugasakhir"]'):
        href = a.attrib.get("href", "").strip()
        title = " ".join(a.text.split()).strip()
        if href and title and href not in seen_urls:
            seen_urls.add(href)
            # Extract id from URL if possible
            m_id = re.search(r"/(?:readbook|tugasakhir)/([^/]+)", href)
            book_id = m_id.group(1) if m_id else str(len(items) + 1)
            
            items.append({
                "id": book_id,
                "title": title,
                "url": href,
            })

    return {
        "total_count": total_count,
        "items": items,
    }

def parse_book_detail(html: str) -> dict[str, Any]:
    page = Adaptor(html)
    data: dict[str, Any] = {
        "kode_buku": None,
        "kode_klasifikasi": None,
        "judul_buku": None,
        "edisi": None,
        "penulis": None,
        "penerbit": None,
        "bahasa": None,
        "tahun": None,
        "isbn": None,
        "tajuk_subjek": None,
        "deskripsi": None,
        "eksemplar": None,
        "stok": None,
        "sinopsis": None,
    }

    key_map = {
        "kode buku": "kode_buku",
        "kode klasifikasi": "kode_klasifikasi",
        "judul buku": "judul_buku",
        "edisi": "edisi",
        "penulis": "penulis",
        "penerbit": "penerbit",
        "bahasa": "bahasa",
        "tahun": "tahun",
        "isbn": "isbn",
        "tajuk subjek": "tajuk_subjek",
        "deskripsi": "deskripsi",
        "eksemplar": "eksemplar",
        "stok": "stok",
    }

    for row in page.css("table tr"):
        cols = [c.text.strip() for c in row.css("td, th")]
        if len(cols) >= 2:
            raw_key = cols[0].lower().replace(":", "").strip()
            val = cols[-1].strip()
            mapped = key_map.get(raw_key)
            if mapped:
                if mapped in ("tahun", "eksemplar", "stok"):
                    data[mapped] = int(val) if val.isdigit() else 0
                elif val == "-":
                    data[mapped] = None
                else:
                    data[mapped] = val

    return data

# ============================================================================
# Client with Slow-Server Exponential Retry (Timeout 60s)
# ============================================================================

class ElibraryClient:
    BASE_URL = "https://elibrary.bsi.ac.id"

    def fetch_search(self, q: str, opsi: str = "buku", page: int = 1) -> str:
        offset = (page - 1) * 10
        safe_q = urllib.parse.quote_plus(q)
        safe_opsi = urllib.parse.quote_plus(opsi)
        url = f"{self.BASE_URL}/opac/pingresult?q={safe_q}&opsi={safe_opsi}&pg={offset}"
        
        last_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                res = Fetcher.get(url, timeout=60, impersonate="chrome")
                if res.status == 200:
                    return res.text if hasattr(res, "text") else res.body.decode("utf-8", "ignore")
            except Exception as e:
                last_error = e
                time.sleep(1.5 * (attempt + 1))

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(
                code="UPSTREAM_TIMEOUT",
                message=f"Layanan elibrary.bsi.ac.id gagal merespons setelah 3 percobaan: {last_error}",
                module="elibrary"
            )
        )

    def fetch_book(self, book_id: str) -> str:
        url = f"{self.BASE_URL}/readbook/{book_id}/detail.html"
        
        last_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                res = Fetcher.get(url, timeout=60, impersonate="chrome")
                if res.status == 200:
                    return res.text if hasattr(res, "text") else res.body.decode("utf-8", "ignore")
            except Exception as e:
                last_error = e
                time.sleep(1.5 * (attempt + 1))

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(
                code="UPSTREAM_TIMEOUT",
                message=f"Gagal mengambil detail buku {book_id}: {last_error}",
                module="elibrary"
            )
        )

elibrary_client = ElibraryClient()

# ============================================================================
# API Routes
# ============================================================================

@router.get("/search")
async def search_books(
    q: str = Query(..., min_length=1, description="Kata kunci pencarian"),
    opsi: str = Query(default="buku", description="Kategori: semua, buku, ta, skripsi, jurnal, prosiding, ebook"),
    page: int = Query(default=1, ge=1, description="Nomor halaman")
):
    cache_key = cache.make_key("elibrary", "search", q=q, opsi=opsi, page=page)

    fresh = await cache.get_fresh(cache_key)
    if fresh is not None:
        return success_response(data=fresh, cached=True)

    async with cache.get_lock(cache_key):
        fresh = await cache.get_fresh(cache_key)
        if fresh is not None:
            return success_response(data=fresh, cached=True)

        try:
            loop = asyncio.get_running_loop()
            html = await loop.run_in_executor(
                None,
                elibrary_client.fetch_search,
                q,
                opsi,
                page
            )
            data = parse_opac_search(html)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="elibrary")
            )

@router.get("/book/{book_id}")
async def get_book_detail(book_id: str = Path(..., pattern=r"^[A-Za-z0-9_-]+$")):
    cache_key = cache.make_key("elibrary", "book", book_id=book_id)

    fresh = await cache.get_fresh(cache_key)
    if fresh is not None:
        return success_response(data=fresh, cached=True)

    async with cache.get_lock(cache_key):
        fresh = await cache.get_fresh(cache_key)
        if fresh is not None:
            return success_response(data=fresh, cached=True)

        try:
            loop = asyncio.get_running_loop()
            html = await loop.run_in_executor(
                None,
                elibrary_client.fetch_book,
                book_id
            )
            data = parse_book_detail(html)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="elibrary")
            )
