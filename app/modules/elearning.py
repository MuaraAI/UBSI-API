import asyncio
import hashlib
import re
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from scrapling.fetchers import FetcherSession
from scrapling.parser import Adaptor

from app.config import settings
from app.deps import require_elearning_creds
from app.envelope import success_response, error_response
from app.cache import cache

router = APIRouter(prefix="/v1/elearning", tags=["elearning"])

# ============================================================================
# Pure Parsers (Unit-tested against snapshot fixtures)
# ============================================================================

def solve_captcha(question_text: str) -> int:
    m = re.search(r"(\d+)\s*\+\s*(\d+)", question_text)
    if not m:
        raise ValueError(f"Tidak dapat menemukan pola captcha matematika di: {question_text}")
    return int(m.group(1)) + int(m.group(2))

def parse_courses(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    plans = page.css("div.pricing-plan")
    courses = []

    for pl in plans:
        title_el = pl.css(".pricing-title")
        nama = title_el[0].text.strip() if title_el else ""

        save_el = pl.css(".pricing-save")
        schedule_text = save_el[0].text.strip() if save_el else ""
        hari, jam = "", ""
        if " - " in schedule_text:
            parts = schedule_text.split(" - ", 1)
            hari, jam = parts[0].strip(), parts[1].strip()
        else:
            hari = schedule_text

        card_text = " ".join(pl.get_all_text().split())
        
        m_dosen = re.search(r"Kode Dosen\s*:\s*([A-Za-z0-9]+)", card_text)
        dosen_code = m_dosen.group(1).strip() if m_dosen else "-"

        m_mtk = re.search(r"Kode MTK\s*:\s*([A-Za-z0-9]+)", card_text)
        kode_mtk = m_mtk.group(1).strip() if m_mtk else ""

        m_sks = re.search(r"SKS\s*:\s*(\d+)", card_text)
        sks = int(m_sks.group(1)) if m_sks else 0

        m_ruang = re.search(r"No Ruang\s*:\s*([A-Za-z0-9\-]+)", card_text)
        ruang = m_ruang.group(1).strip() if m_ruang else ""

        m_kel = re.search(r"Kel Praktek\s*:\s*([A-Za-z0-9\.\-]+)", card_text)
        kel_praktek = m_kel.group(1).strip() if m_kel else None

        m_gabung = re.search(r"Kode Gabung\s*:\s*([A-Za-z0-9\.\-]+)", card_text)
        kode_gabung = m_gabung.group(1).strip() if m_gabung else None

        # Extract encrypted tokens
        def extract_token(pattern: str) -> Optional[str]:
            for a in pl.css("a"):
                href = a.attrib.get("href", "")
                if pattern in href:
                    return href.split(pattern)[-1]
            return None

        token_absen = extract_token("/absen-mhs/")
        token_diskusi = extract_token("/form-diskusimhs/")
        token_learning = extract_token("/learning/")
        token_assignment = extract_token("/assignment/")

        item_id = hashlib.sha256(f"{kode_mtk}:{token_absen}".encode()).hexdigest()[:12]

        courses.append({
            "id": item_id,
            "kode": kode_mtk,
            "nama": nama,
            "sks": sks,
            "hari": hari,
            "jam": jam,
            "ruang": ruang,
            "kode_dosen": dosen_code,
            "kelompok_praktek": kel_praktek,
            "kode_gabung": kode_gabung,
            "token_absen": token_absen,
            "token_diskusi": token_diskusi,
            "token_learning": token_learning,
            "token_assignment": token_assignment,
        })

    return courses

def parse_assignments(html: str) -> dict[str, list[dict[str, Any]]]:
    page = Adaptor(html)
    tables = page.css("table")
    tasks = []
    submissions = []

    # Table 0: Tasks
    if len(tables) >= 1:
        for r in tables[0].css("tr")[1:]:
            cols = [c.text.strip() for c in r.css("td")]
            if len(cols) >= 8:
                item_id = hashlib.sha256(f"{cols[1]}:{cols[3]}:{cols[5]}".encode()).hexdigest()[:12]
                tasks.append({
                    "id": item_id,
                    "kode": cols[1],
                    "kelas": cols[2],
                    "judul": cols[3],
                    "deskripsi": cols[4],
                    "pertemuan": cols[5],
                    "mulai": cols[6],
                    "selesai": cols[7],
                })

    # Table 1: Submissions
    if len(tables) >= 2:
        for r in tables[1].css("tr")[1:]:
            cols = [c.text.strip() for c in r.css("td")]
            links = [a.attrib.get("href") for a in r.css("a") if a.attrib.get("href")]
            if len(cols) >= 7:
                item_id = hashlib.sha256(f"{cols[1]}:{cols[2]}:{cols[3]}".encode()).hexdigest()[:12]
                submissions.append({
                    "id": item_id,
                    "kode": cols[1],
                    "judul": cols[2],
                    "pertemuan": cols[3],
                    "link_tugas": links[0] if links else cols[4],
                    "komentar_dosen": cols[5] if cols[5] else None,
                    "nilai": float(cols[6]) if cols[6] and cols[6].replace(".", "").isdigit() else None,
                })

    return {"tasks": tasks, "submissions": submissions}

def parse_presence(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    tables = page.css("table")
    records = []

    target_table = None
    for t in tables:
        h_text = " ".join([c.text.strip() for c in t.css("th")])
        if "Status Absen" in h_text or "Pertemuan" in h_text:
            target_table = t
            break

    if target_table:
        for r in target_table.css("tr")[1:]:
            cols = [c.text.strip() for c in r.css("td")]
            if len(cols) >= 6:
                item_id = hashlib.sha256(f"{cols[2]}:{cols[4]}".encode()).hexdigest()[:12]
                records.append({
                    "id": item_id,
                    "status_absen": cols[1],
                    "tanggal": cols[2],
                    "matakuliah": cols[3],
                    "pertemuan": cols[4],
                    "rangkuman": cols[5] if cols[5] else None,
                    "berita_acara": cols[6] if len(cols) > 6 and cols[6] else None,
                })

    return records

def parse_materials(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    materials = []

    # Check table rows first
    tables = page.css("table")
    if tables:
        for r in tables[0].css("tr")[1:]:
            cols = [c.text.strip() for c in r.css("td")]
            links = [a.attrib.get("href") for a in r.css("a") if a.attrib.get("href")]
            if len(cols) >= 5:
                item_id = hashlib.sha256(f"{cols[1]}:{cols[3]}".encode()).hexdigest()[:12]
                materials.append({
                    "id": item_id,
                    "kode": cols[1],
                    "kelas": cols[2],
                    "judul": cols[3],
                    "deskripsi": cols[4],
                    "file_url": links[0] if links else None,
                    "update": cols[6] if len(cols) > 6 else None,
                })

    # Also capture any standalone download links (silabus / modul zip)
    seen_urls = {m["file_url"] for m in materials if m.get("file_url")}
    for a in page.css("a"):
        h = a.attrib.get("href", "").strip()
        if h and any(ext in h.lower() for ext in [".zip", ".pdf", ".rar", "silabus"]):
            if h not in seen_urls:
                seen_urls.add(h)
                title = a.text.strip() or ("Silabus / Modul" if "silabus" in h else "Bahan Ajar")
                item_id = hashlib.sha256(h.encode()).hexdigest()[:12]
                materials.append({
                    "id": item_id,
                    "kode": None,
                    "kelas": None,
                    "judul": title,
                    "deskripsi": "Berkas silabus / modul pembelajaran",
                    "file_url": h,
                    "update": None,
                })

    return materials

def parse_quiz(html: str) -> list[dict[str, Any]]:
    page = Adaptor(html)
    quizzes = []
    rows = page.css("table tr")
    for r in rows[1:]:
        cols = [c.text.strip() for c in r.css("td")]
        if len(cols) >= 7:
            item_id = hashlib.sha256(f"{cols[2]}:{cols[5]}".encode()).hexdigest()[:12]
            quizzes.append({
                "id": item_id,
                "kode_mtk": cols[1] if cols[1] else None,
                "paket": cols[2],
                "dosen": cols[3] if cols[3] else None,
                "waktu": cols[4] if cols[4] else None,
                "ujian_mulai": cols[5],
                "ujian_selesai": cols[6],
            })
    return quizzes

# ============================================================================
# Authenticated Scrapling Client
# ============================================================================

class ElearningClient:
    BASE_URL = "https://elearning.bsi.ac.id"

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

            # Extract and solve math captcha
            q_el = r1.css("#captcha_question")
            q_text = q_el[0].text if q_el else r1.text
            ans = solve_captcha(q_text)

            payload = {
                "_token": token,
                "username": nim,
                "password": password,
                "captcha_answer": str(ans),
            }
            r2 = session.post(login_url, data=payload, timeout=20)
            if "dashboard" in str(r2.url) or "elearning.bsi.ac.id/user" in str(r2.url) or r2.status == 200:
                self._logged_in = True
                return True
            return False
        except Exception:
            return False

    def fetch_page(self, path: str, nim: str, password: str) -> str:
        session = self.get_session()
        target_url = f"{self.BASE_URL}{path}" if path.startswith("/") else path

        if not self._logged_in:
            ok = self.login(nim, password)
            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=error_response(
                        code="AUTH_FAILED",
                        message="Gagal login ke elearning.bsi.ac.id (captcha/kredensial salah)",
                        module="elearning"
                    )
                )

        r = session.get(target_url, timeout=30)

        # Handle session expiration
        if "/login" in str(r.url):
            ok = self.login(nim, password)
            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=error_response(
                        code="AUTH_EXPIRED",
                        message="Sesi login elearning kedaluwarsa dan gagal login ulang",
                        module="elearning"
                    )
                )
            r = session.get(target_url, timeout=30)

        return r.text if hasattr(r, "text") else r.body.decode("utf-8", "ignore")

elearning_client = ElearningClient()

# ============================================================================
# API Routes
# ============================================================================

@router.get("/courses")
async def get_courses(creds: tuple[str, str] = Depends(require_elearning_creds)):
    nim, password = creds
    cache_key = cache.make_key("elearning", "courses", nim=nim)

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
                elearning_client.fetch_page,
                "/sch",
                nim,
                password
            )
            data = parse_courses(html)
            await cache.set(cache_key, data, ttl=settings.TTL_ASSIGNMENTS)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="elearning")
            )

@router.get("/assignments")
async def get_assignments(
    token: Optional[str] = Query(default=None, pattern=r"^[A-Za-z0-9+/=_-]+$", description="Encrypted course token from /courses"),
    creds: tuple[str, str] = Depends(require_elearning_creds)
):
    nim, password = creds
    
    # If no token provided, get courses first and use first course's token
    if not token:
        courses_res = await get_courses(creds)
        courses = courses_res["data"]
        if not courses or not courses[0].get("token_assignment"):
            return success_response(data={"tasks": [], "submissions": []}, cached=False)
        token = courses[0]["token_assignment"]

    cache_key = cache.make_key("elearning", "assignments", token=token)

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
                elearning_client.fetch_page,
                f"/assignment/{token}",
                nim,
                password
            )
            data = parse_assignments(html)
            await cache.set(cache_key, data, ttl=settings.TTL_ASSIGNMENTS)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="elearning")
            )

@router.get("/presence")
async def get_presence(
    token: Optional[str] = Query(default=None, pattern=r"^[A-Za-z0-9+/=_-]+$", description="Encrypted course token from /courses"),
    creds: tuple[str, str] = Depends(require_elearning_creds)
):
    nim, password = creds

    if not token:
        courses_res = await get_courses(creds)
        courses = courses_res["data"]
        if not courses or not courses[0].get("token_absen"):
            return success_response(data=[], cached=False)
        token = courses[0]["token_absen"]

    cache_key = cache.make_key("elearning", "presence", token=token)

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
                elearning_client.fetch_page,
                f"/absen-mhs/{token}",
                nim,
                password
            )
            data = parse_presence(html)
            await cache.set(cache_key, data, ttl=settings.TTL_ASSIGNMENTS)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="elearning")
            )

@router.get("/materials")
async def get_materials(
    token: Optional[str] = Query(default=None, pattern=r"^[A-Za-z0-9+/=_-]+$", description="Encrypted course token from /courses"),
    creds: tuple[str, str] = Depends(require_elearning_creds)
):
    nim, password = creds

    if not token:
        courses_res = await get_courses(creds)
        courses = courses_res["data"]
        if not courses or not courses[0].get("token_learning"):
            return success_response(data=[], cached=False)
        token = courses[0]["token_learning"]

    cache_key = cache.make_key("elearning", "materials", token=token)

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
                elearning_client.fetch_page,
                f"/learning/{token}",
                nim,
                password
            )
            data = parse_materials(html)
            await cache.set(cache_key, data, ttl=settings.TTL_ASSIGNMENTS)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="elearning")
            )

@router.get("/quiz")
async def get_quiz(creds: tuple[str, str] = Depends(require_elearning_creds)):
    nim, password = creds
    cache_key = cache.make_key("elearning", "quiz", nim=nim)

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
                elearning_client.fetch_page,
                "/exercise",
                nim,
                password
            )
            data = parse_quiz(html)
            await cache.set(cache_key, data, ttl=settings.TTL_ASSIGNMENTS)
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
                detail=error_response(code="UPSTREAM_ERROR", message=str(e), module="elearning")
            )
