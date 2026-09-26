import asyncio
import hashlib
import re
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from scrapling.fetchers import FetcherSession
from scrapling.parser import Adaptor

from app.config import settings
from app.deps import require_studentv2_creds
from app.envelope import success_response, error_response
from app.cache import cache

router = APIRouter(prefix="/v1/studentv2", tags=["studentv2"])

# ============================================================================
# Pure Parsers (Unit-tested against snapshot fixtures)
# ============================================================================

def parse_schedule(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    rows = page.css("table tr")
    results = []
    for row in rows[1:]:
        cols = [c.text.strip() for c in row.css("td")]
        if len(cols) >= 9:
            raw_dosen = cols[3].replace("\n", " ").strip()
            dosen_code = raw_dosen.split("/")[0].strip() if "/" in raw_dosen else (raw_dosen.split()[0] if raw_dosen.split() else "-")
            item_id = hashlib.sha256(f"{cols[4]}:{cols[1]}:{cols[2]}".encode()).hexdigest()[:12]
            results.append({
                "id": item_id,
                "kode": cols[4],
                "nama": cols[5],
                "hari": cols[1],
                "jam": cols[2],
                "sks": int(cols[6]) if cols[6].isdigit() else 0,
                "kelompok_praktek": cols[7] if cols[7] else None,
                "ruang": cols[8],
                "kode_dosen": dosen_code,
            })
    return results

def parse_grades(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    rows = page.css("table tr")
    results = []
    for row in rows[1:]:
        cols = [c.text.strip() for c in row.css("td")]
        if len(cols) >= 10:
            item_id = hashlib.sha256(cols[1].encode()).hexdigest()[:12]
            
            def to_float(val: str) -> Optional[float]:
                if not val or val == "-":
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None

            results.append({
                "id": item_id,
                "kode": cols[1],
                "nama": cols[2],
                "sks": int(cols[3]) if cols[3].isdigit() else 0,
                "uts": to_float(cols[4]),
                "uas": to_float(cols[5]),
                "tugas": to_float(cols[6]),
                "absen": to_float(cols[7]),
                "total": to_float(cols[8]),
                "grade": cols[9] if cols[9] else None,
            })
    return results

def parse_news(html: str, limit: int = 100) -> list[dict[str, Any]]:
    page = Adaptor(html)
    rows = page.css("table tr")
    results = []
    for row in rows[1:]:
        cols = [c.text.strip() for c in row.css("td")]
        links = [a.attrib.get("href") for a in row.css("a") if a.attrib.get("href")]
        if len(cols) >= 4 and links:
            item_id = hashlib.sha256(cols[1].encode()).hexdigest()[:12]
            results.append({
                "id": item_id,
                "title": cols[1],
                "pdf_url": links[0],
                "date": cols[3],
            })
            if len(results) >= limit:
                break
    return results

def parse_announcements(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    results = []
    links = page.css('a[href*="pengumuman_dalam_"]')
    seen_urls = set()
    for a in links:
        title = " ".join(a.text.split()).strip()
        url = a.attrib.get("href", "").strip()
        if title and url and url not in seen_urls:
            seen_urls.add(url)
            item_id = hashlib.sha256(url.encode()).hexdigest()[:12]
            results.append({
                "id": item_id,
                "title": title,
                "pdf_url": url,
            })
    return results

# ============================================================================
# Authenticated Client Session
# ============================================================================

class StudentV2Client:
    BASE_URL = "https://studentv2.bsi.ac.id"

    def __init__(self):
        self._session_ctx: Optional[FetcherSession] = None
        self._session: Any = None
        self._logged_in: bool = False
        self._login_lock = asyncio.Lock()

    def get_session(self) -> Any:
        if self._session is None:
            self._session_ctx = FetcherSession(impersonate="chrome")
            self._session = self._session_ctx.__enter__()
        return self._session

    def close(self) -> None:
        if self._session_ctx is not None:
            try:
                self._session_ctx.__exit__(None, None, None)
            except Exception:
                pass
            self._session = None
            self._session_ctx = None
            self._logged_in = False

    def login(self, nim: str, password: str) -> bool:
        session = self.get_session()
        login_url = f"{self.BASE_URL}/login"
        try:
            r1 = session.get(login_url, timeout=20)
            token_el = r1.css('input[name="_token"]')
            if not token_el:
                return False
            token = token_el[0].attrib.get("value")

            payload = {
                "_token": token,
                "username": nim,
                "password": password,
                "remember": "on"
            }
            r2 = session.post(login_url, data=payload, timeout=20)
            if "mahasiswa/beranda" in str(r2.url) or "studentv2.bsi.ac.id/mahasiswa" in str(r2.url):
                self._logged_in = True
                return True
            return False
        except Exception:
            return False

    def fetch_page(self, path: str, nim: str, password: str) -> str:
        session = self.get_session()
        target_url = f"{self.BASE_URL}{path}"
        
        if not self._logged_in:
            ok = self.login(nim, password)
            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=error_response(
                        code="AUTH_FAILED",
                        message="Gagal login ke studentv2.bsi.ac.id",
                        module="studentv2"
                    )
                )

        r = session.get(target_url, timeout=25)
        
        # Check if redirected to login (expired session)
        if "/login" in str(r.url):
            ok = self.login(nim, password)
            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=error_response(
                        code="AUTH_EXPIRED",
                        message="Sesi login studentv2 kedaluwarsa dan gagal login ulang",
                        module="studentv2"
                    )
                )
            r = session.get(target_url, timeout=25)

        return r.text if hasattr(r, "text") else r.body.decode("utf-8", "ignore")

studentv2_client = StudentV2Client()

# ============================================================================
# API Routes
# ============================================================================

@router.get("/schedule")
async def get_schedule(creds: tuple[str, str] = Depends(require_studentv2_creds)):
    nim, password = creds
    cache_key = cache.make_key("studentv2", "schedule", nim=nim)
    
    # 1. Check fresh cache
    fresh = await cache.get_fresh(cache_key)
    if fresh is not None:
        return success_response(data=fresh, cached=True)

    # 2. Mutex single-flight lock
    async with cache.get_lock(cache_key):
        fresh = await cache.get_fresh(cache_key)
        if fresh is not None:
            return success_response(data=fresh, cached=True)

        try:
            loop = asyncio.get_running_loop()
            html = await loop.run_in_executor(
                None,
                studentv2_client.fetch_page,
                "/mahasiswa/jadwal-kuliah",
                nim,
                password
            )
            data = parse_schedule(html)
            await cache.set(cache_key, data, ttl=settings.TTL_SCHEDULE)
            return success_response(data=data, cached=False)
        except Exception as e:
            # Check LGG fallback
            lgg_result = await cache.get_lgg(cache_key)
            if lgg_result:
                lgg_data, _ = lgg_result
                return success_response(data=lgg_data, cached=True, stale=True)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="studentv2")
            )

@router.get("/grades")
async def get_grades(creds: tuple[str, str] = Depends(require_studentv2_creds)):
    nim, password = creds
    cache_key = cache.make_key("studentv2", "grades", nim=nim)

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
                studentv2_client.fetch_page,
                "/mahasiswa/nilai-murni",
                nim,
                password
            )
            data = parse_grades(html)
            await cache.set(cache_key, data, ttl=settings.TTL_GRADES)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="studentv2")
            )

@router.get("/news")
async def get_news(
    limit: int = Query(default=50, ge=1, le=200),
    creds: tuple[str, str] = Depends(require_studentv2_creds)
):
    nim, password = creds
    cache_key = cache.make_key("studentv2", "news", limit=limit)

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
                studentv2_client.fetch_page,
                "/mahasiswa/berita",
                nim,
                password
            )
            data = parse_news(html, limit=limit)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="studentv2")
            )

@router.get("/announcements")
async def get_announcements(creds: tuple[str, str] = Depends(require_studentv2_creds)):
    nim, password = creds
    cache_key = cache.make_key("studentv2", "announcements")

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
                studentv2_client.fetch_page,
                "/mahasiswa/beranda",
                nim,
                password
            )
            data = parse_announcements(html)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="studentv2")
            )
