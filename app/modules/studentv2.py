import asyncio
import hashlib
import re
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from scrapling.parser import Adaptor

from app.config import settings
from app.deps import require_studentv2_creds
from app.envelope import success_response, error_response
from app.cache import cache
from app.session_pool import SessionPool
from app.retry import retry_async

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
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Origin": "https://studentv2.bsi.ac.id",
        "Referer": "https://studentv2.bsi.ac.id/login",
    }

    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self._logged_in: bool = False
        self._login_lock = asyncio.Lock()

    def get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(headers=self.HEADERS, follow_redirects=True, timeout=25.0)
        return self._client

    def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
            self._logged_in = False

    def login(self, nim: str, password: str) -> bool:
        client = self.get_client()
        login_url = f"{self.BASE_URL}/login"
        try:
            r1 = client.get(login_url)
            m = re.search(r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', r1.text)
            if not m:
                return False
            token = m.group(1)

            payload = {
                "_token": token,
                "username": nim,
                "password": password,
                "remember": "on"
            }
            r2 = client.post(login_url, data=payload)
            if "mahasiswa/beranda" in str(r2.url) or "studentv2.bsi.ac.id/mahasiswa" in str(r2.url):
                self._logged_in = True
                return True
            return False
        except Exception:
            return False

    def fetch_page(self, path: str, nim: str, password: str) -> str:
        client = self.get_client()
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

        r = client.get(target_url)
        
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
            r = client.get(target_url)

        return r.text

class PooledStudentV2Client:
    """Fasade client dengan pool sesi per-NIM.

    Dua NIM berbeda yang memanggil bersamaan tidak lagi saling menimpa sesi:
    setiap NIM mendapat instance StudentV2Client sendiri di dalam pool, dan
    sesi idle ditutup oleh evict_idle.
    """

    def __init__(self, ttl_seconds: int = 900):
        self._pool = SessionPool(lambda: StudentV2Client(), ttl_seconds=ttl_seconds)

    async def fetch_page(self, path: str, nim: str, password: str) -> str:
        client = self._pool.get(nim)

        def _fetch_once() -> str:
            return client.fetch_page(path, nim, password)

        try:
            return await retry_async(_fetch_once, attempts=3, base_delay=1.0)
        except HTTPException as exc:
            # Login expired → buang sesi supaya request berikutnya login ulang
            detail = getattr(exc, "detail", None)
            if isinstance(detail, dict) and detail.get("code") == "AUTH_EXPIRED":
                self._pool.invalidate(nim)
            raise

    async def evict_idle(self) -> int:
        return await self._pool.evict_idle()

    def close(self) -> None:
        for nim in list(self._pool._sessions.keys()):
            self._pool.invalidate(nim)


studentv2_client = PooledStudentV2Client()

# ============================================================================
# API Routes
# ============================================================================

@router.get("/schedule")
async def get_schedule(creds: tuple[str, str] = Depends(require_studentv2_creds)):
    nim, password = creds
    cache_key = cache.make_key("studentv2", "schedule", nim=nim)

    # 1. Stale-while-revalidate: LGG dikirim instan, refresh jalan di belakang
    cached = await cache.fresh_or_stale(cache_key)
    if cached is not None:
        data, is_stale = cached
        if is_stale:
            async def _revalidate():
                try:
                    html = await studentv2_client.fetch_page(
                        "/mahasiswa/jadwal-kuliah", nim, password
                    )
                    parsed = parse_schedule(html)
                    await cache.set(cache_key, parsed, ttl=settings.TTL_SCHEDULE)
                except Exception:
                    pass

            asyncio.create_task(_revalidate())
            return success_response(data=data, cached=True, stale=True)
        return success_response(data=data, cached=True)

    # 2. Mutex single-flight lock
    async with cache.get_lock(cache_key):
        cached = await cache.fresh_or_stale(cache_key)
        if cached is not None:
            data, is_stale = cached
            if is_stale:
                return success_response(data=data, cached=True, stale=True)
            return success_response(data=data, cached=True)

        try:
            html = await studentv2_client.fetch_page(
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
            html = await studentv2_client.fetch_page(
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
            html = await studentv2_client.fetch_page(
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
            html = await studentv2_client.fetch_page(
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


@router.get("/dashboard")
async def get_dashboard(creds: tuple[str, str] = Depends(require_studentv2_creds)):
    """Ambil jadwal + nilai + berita + pengumuman sekaligus secara paralel.

    Total waktu respons = halaman upstream paling lambat, bukan jumlah
    keempatnya. Data yang sudah ada di cache tidak memicu fetch ulang.
    """
    nim, password = creds

    async def _section(name: str, path: str, parser, ttl: int):
        cache_key = cache.make_key("studentv2", name, nim=nim)
        fresh = await cache.get_fresh(cache_key)
        if fresh is not None:
            return name, success_response(data=fresh, cached=True), cache_key
        try:
            html = await studentv2_client.fetch_page(
                path,
                nim,
                password,
            )
            data = parser(html)
            await cache.set(cache_key, data, ttl=ttl)
            return name, success_response(data=data, cached=False), cache_key
        except Exception as e:
            lgg_result = await cache.get_lgg(cache_key)
            if lgg_result:
                lgg_data, _ = lgg_result
                return name, success_response(data=lgg_data, cached=True, stale=True), cache_key
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="studentv2")
            )

    results = await asyncio.gather(
        _section("schedule", "/mahasiswa/jadwal-kuliah", parse_schedule, settings.TTL_SCHEDULE),
        _section("grades", "/mahasiswa/nilai-murni", parse_grades, settings.TTL_GRADES),
        _section("news", "/mahasiswa/berita", parse_news, settings.TTL_NEWS),
        _section("announcements", "/mahasiswa/beranda", parse_announcements, settings.TTL_NEWS),
        return_exceptions=True,
    )

    dashboard: dict[str, Any] = {}
    all_cached = True
    errors: list[str] = []
    for item in results:
        if isinstance(item, Exception):
            errors.append(str(item))
            continue
        name, response, _ = item
        dashboard[name] = response["data"]
        if not response.get("cached"):
            all_cached = False

    if not dashboard and errors:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=error_response(code="UPSTREAM_ERROR", message="; ".join(errors), module="studentv2")
        )

    return success_response(data=dashboard, cached=all_cached)
