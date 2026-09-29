import asyncio
import hashlib
import re
import statistics
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from scrapling.parser import Adaptor

from app.config import settings
from app.deps import require_elearning_creds
from app.envelope import success_response, error_response
from app.session_pool import SessionPool
from app.retry import retry_async
from app.router_helper import cached_endpoint

router = APIRouter(prefix="/v1/elearning", tags=["elearning"])

# ============================================================================
# Pure Parsers (Unit-tested against snapshot fixtures)
# ============================================================================

def solve_captcha(question_text: str) -> Any:
    # 1. New SVG text captcha (<text ...>X</text>)
    svg_texts = re.findall(r"<text[^>]*>([^<]+)</text>", question_text)
    if svg_texts:
        return "".join(svg_texts).strip()

    # 2. Legacy math pattern ("12 + 5")
    m = re.search(r"(\d+)\s*\+\s*(\d+)", question_text)
    if m:
        return int(m.group(1)) + int(m.group(2))

    raise ValueError(f"Tidak dapat menemukan pola captcha di: {question_text[:100]}")

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

        m_kel = re.search(r"Kel Praktek\s*:\s*(?!Kode\b)([A-Za-z0-9\.\-]+)", card_text)
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

        item_id = hashlib.sha256(f"{kode_mtk}:{hari}:{jam}:{ruang}".encode()).hexdigest()[:12]

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
            "jadwal": {
                "hari": hari,
                "jam": jam,
                "ruang": ruang,
            },
            "tokens": {
                "absen": token_absen,
                "diskusi": token_diskusi,
                "learning": token_learning,
                "assignment": token_assignment,
            },
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

def parse_presence(html: str) -> dict[str, Any]:
    page = Adaptor(html)
    tiles = page.css("div.info-tiles")
    info: dict[str, str] = {}
    for t in tiles:
        detail = t.css(".stats-detail")
        if detail:
            val = detail[0].css("h5")
            label = detail[0].css("p")
            if val and label:
                info[label[0].text.strip().lower()] = val[0].text.strip()

    btn = page.css("div.col-xl-3 button, button.btn-warning, button.btn-success, button.btn-info, button.btn-danger")
    status_sesi = btn[0].text.strip() if btn else None

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

    return {
        "kode_mtk": info.get("kode mtk"),
        "matakuliah": info.get("matakuliah"),
        "kelas": info.get("kelas"),
        "dosen": info.get("dosen"),
        "ruang": info.get("ruang"),
        "hari": info.get("hari"),
        "jam_masuk": info.get("jam masuk"),
        "jam_keluar": info.get("jam keluar"),
        "status_sesi": status_sesi,
        "total_kehadiran": len(records),
        "riwayat": records,
    }

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
# Rekap Nilai (Per Pertemuan)
# ============================================================================

def _pertemuan_sort_key(pertemuan: str) -> int:
    digits = [int(n) for n in re.findall(r"\d+", str(pertemuan))]
    return digits[0] if digits else 999

def _to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    cleaned = value.strip().replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None

def summarize_grades(
    submissions: list[dict[str, Any]],
    quizzes: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Rekap status & statistik nilai tugas (dan kuis) per pertemuan.

    submissions: hasil parse_assignments()["submissions"] (satu mata kuliah
    atau gabungan beberapa matkul, dibedakan lewat kolom "kode").
    quizzes: hasil parse_quiz() opsional untuk pelengkap status ujian.
    """
    quizzes = quizzes or []

    by_pertemuan: dict[str, list[dict[str, Any]]] = {}
    for s in submissions:
        by_pertemuan.setdefault(s.get("pertemuan") or "-", []).append(s)

    pertemuan_rows = []
    for pert, items in by_pertemuan.items():
        graded = [s["nilai"] for s in items if isinstance(s.get("nilai"), (int, float))]
        pertemuan_rows.append({
            "pertemuan": pert,
            "total_tugas": len(items),
            "sudah_dinilai": len(graded),
            "belum_dinilai": len(items) - len(graded),
            "rata_nilai": round(statistics.fmean(graded), 2) if graded else None,
            "nilai_max": max(graded) if graded else None,
            "nilai_min": min(graded) if graded else None,
            "items": items,
        })
    pertemuan_rows.sort(key=lambda r: _pertemuan_sort_key(r["pertemuan"]))

    all_graded = [s["nilai"] for s in submissions if isinstance(s.get("nilai"), (int, float))]
    by_course: dict[str, list[float]] = {}
    for s in submissions:
        nilai = s.get("nilai")
        if isinstance(nilai, (int, float)):
            by_course.setdefault(s.get("kode") or "-", []).append(nilai)

    return {
        "total_tugas": len(submissions),
        "sudah_dinilai": len(all_graded),
        "belum_dinilai": len(submissions) - len(all_graded),
        "rata_nilai": round(statistics.fmean(all_graded), 2) if all_graded else None,
        "nilai_max": max(all_graded) if all_graded else None,
        "nilai_min": min(all_graded) if all_graded else None,
        "per_matkul": {
            kode: {
                "total_tugas": len(nilais),
                "rata_nilai": round(statistics.fmean(nilais), 2),
            }
            for kode, nilais in sorted(by_course.items())
        },
        "per_pertemuan": pertemuan_rows,
        "kuis": [
            {
                "paket": q.get("paket"),
                "kode_mtk": q.get("kode_mtk"),
                "dosen": q.get("dosen"),
                "ujian_mulai": q.get("ujian_mulai"),
                "ujian_selesai": q.get("ujian_selesai"),
            }
            for q in quizzes
        ],
    }

# ============================================================================
# Authenticated Scrapling Client
# ============================================================================

class ElearningClient:
    BASE_URL = "https://elearning.bsi.ac.id"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Origin": "https://elearning.bsi.ac.id",
        "Referer": "https://elearning.bsi.ac.id/login",
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

            try:
                ans = solve_captcha(r1.text)
            except ValueError:
                return False

            payload = {
                "_token": token,
                "username": nim,
                "password": password,
                "captcha_answer": str(ans),
            }
            r2 = client.post(login_url, data=payload)
            if "dashboard" in str(r2.url) or "elearning.bsi.ac.id/user" in str(r2.url):
                self._logged_in = True
                return True
            return False
        except Exception:
            return False

    def fetch_page(self, path: str, nim: str, password: str) -> str:
        client = self.get_client()
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

        r = client.get(target_url)

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
            r = client.get(target_url)

        return r.text

elearning_client = ElearningClient()


class PooledElearningClient:
    """Fasade client elearning dengan pool sesi per-NIM (pola sama studentv2)."""

    def __init__(self, ttl_seconds: int = 900):
        self._pool = SessionPool(lambda: ElearningClient(), ttl_seconds=ttl_seconds)

    async def fetch_page(self, path: str, nim: str, password: str) -> str:
        client = self._pool.get(nim)

        def _fetch_once() -> str:
            return client.fetch_page(path, nim, password)

        try:
            return await retry_async(_fetch_once, attempts=3, base_delay=1.0)
        except HTTPException as exc:
            detail = getattr(exc, "detail", None)
            if isinstance(detail, dict) and detail.get("code") == "AUTH_EXPIRED":
                self._pool.invalidate(nim)
            raise

    async def evict_idle(self) -> int:
        return await self._pool.evict_idle()

    def close(self) -> None:
        for nim in list(self._pool._sessions.keys()):
            self._pool.invalidate(nim)


pooled_elearning_client = PooledElearningClient()

# ============================================================================
# API Routes
# ============================================================================

@router.get("/courses")
async def get_courses(creds: tuple[str, str] = Depends(require_elearning_creds)):
    nim, password = creds
    return await cached_endpoint(
        module="elearning",
        name="courses",
        fetch=lambda: pooled_elearning_client.fetch_page("/sch", nim, password),
        parse=parse_courses,
        ttl=settings.TTL_ASSIGNMENTS,
        cache_params={"nim": nim},
    )

@router.get("/assignments")
async def get_assignments(
    token: Optional[str] = Query(default=None, pattern=r"^[A-Za-z0-9+/=_-]+$", description="Encrypted course token from /courses (opsional, tanpa token = agregasi seluruh matkul)"),
    creds: tuple[str, str] = Depends(require_elearning_creds)
):
    nim, password = creds

    if not token:
        async def _fetch_all_assignments():
            courses_res = await get_courses(creds)
            courses = courses_res["data"]

            async def _fetch_for(course: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
                t = course.get("token_assignment")
                if not t:
                    return {"tasks": [], "submissions": []}
                try:
                    html = await pooled_elearning_client.fetch_page(f"/assignment/{t}", nim, password)
                    parsed = parse_assignments(html)
                    for item in parsed.get("tasks", []):
                        item.setdefault("kode", course.get("kode") or "")
                        item["mata_kuliah"] = course.get("nama") or ""
                    for item in parsed.get("submissions", []):
                        item.setdefault("kode", course.get("kode") or "")
                        item["mata_kuliah"] = course.get("nama") or ""
                    return parsed
                except Exception:
                    return {"tasks": [], "submissions": []}

            results = await asyncio.gather(*(_fetch_for(c) for c in courses), return_exceptions=True)
            tasks_list: list[dict[str, Any]] = []
            submissions_list: list[dict[str, Any]] = []
            for r in results:
                if isinstance(r, dict):
                    tasks_list.extend(r.get("tasks", []))
                    submissions_list.extend(r.get("submissions", []))
            return {"tasks": tasks_list, "submissions": submissions_list}

        return await cached_endpoint(
            module="elearning",
            name="assignments",
            fetch=_fetch_all_assignments,
            parse=lambda data: data,
            ttl=settings.TTL_ASSIGNMENTS,
            cache_params={"nim": nim, "token": "all"},
        )

    return await cached_endpoint(
        module="elearning",
        name="assignments",
        fetch=lambda: pooled_elearning_client.fetch_page(f"/assignment/{token}", nim, password),
        parse=parse_assignments,
        ttl=settings.TTL_ASSIGNMENTS,
        cache_params={"token": token},
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
            return success_response(data={}, cached=False)
        token = courses[0]["token_absen"]

    return await cached_endpoint(
        module="elearning",
        name="presence",
        fetch=lambda: pooled_elearning_client.fetch_page(f"/absen-mhs/{token}", nim, password),
        parse=parse_presence,
        ttl=settings.TTL_ASSIGNMENTS,
        cache_params={"token": token},
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

    return await cached_endpoint(
        module="elearning",
        name="materials",
        fetch=lambda: pooled_elearning_client.fetch_page(f"/learning/{token}", nim, password),
        parse=parse_materials,
        ttl=settings.TTL_ASSIGNMENTS,
        cache_params={"token": token},
    )

@router.get("/quiz")
async def get_quiz(creds: tuple[str, str] = Depends(require_elearning_creds)):
    nim, password = creds
    return await cached_endpoint(
        module="elearning",
        name="quiz",
        fetch=lambda: pooled_elearning_client.fetch_page("/exercise", nim, password),
        parse=parse_quiz,
        ttl=settings.TTL_ASSIGNMENTS,
        cache_params={"nim": nim},
    )

# ============================================================================
# Rekap Nilai Tugas & Kuis (Per Pertemuan)
# ============================================================================

async def _build_grades(
    nim: str,
    password: str,
    token: Optional[str],
) -> dict[str, Any]:
    """Kumpulkan submissions (opsional per-token) + daftar kuis, lalu rekap.

    Tanpa token: submissions digabung dari seluruh mata kuliah aktif
    (halaman /assignment/{token_assignment} per kursus dari /sch).
    """
    quiz_res = await get_quiz((nim, password))
    quizzes = quiz_res["data"]

    if token:
        assignment_res = await get_assignments(token=token, creds=(nim, password))
        submissions = assignment_res["data"]["submissions"]
    else:
        courses_res = await get_courses((nim, password))
        courses = courses_res["data"]

        async def _subs_for(course: dict[str, Any]) -> list[dict[str, Any]]:
            t = course.get("token_assignment")
            if not t:
                return []
            res = await get_assignments(token=t, creds=(nim, password))
            subs = res["data"]["submissions"]
            for s in subs:
                s.setdefault("kode", course.get("kode") or "-")
                s["mata_kuliah"] = course.get("nama") or ""
            return subs

        gathered = await asyncio.gather(
            *(_subs_for(c) for c in courses), return_exceptions=True
        )
        submissions: list[dict[str, Any]] = []
        for item in gathered:
            if isinstance(item, BaseException):
                continue
            submissions.extend(item)

    return summarize_grades(submissions, quizzes)


@router.get("/grades")
async def get_grades(
    token: Optional[str] = Query(default=None, pattern=r"^[A-Za-z0-9+/=_-]+$", description="Encrypted course token from /courses (opsional, tanpa token = semua matkul)"),
    creds: tuple[str, str] = Depends(require_elearning_creds),
):
    """Rekap nilai tugas & kuis seluruh mata kuliah aktif, per pertemuan."""
    nim, password = creds

    return await cached_endpoint(
        module="elearning",
        name="grades",
        fetch=lambda: _build_grades(nim, password, token),
        parse=lambda data: data,
        ttl=settings.TTL_GRADES,
        cache_params={"nim": nim, "token": token or "all"},
    )


@router.get("/courses/{course_id}/grades")
async def get_course_grades(
    course_id: str,
    creds: tuple[str, str] = Depends(require_elearning_creds),
):
    """Rekap nilai tugas & kuis satu mata kuliah (id dari /v1/elearning/courses)."""
    nim, password = creds

    courses_res = await get_courses(creds)
    courses = courses_res["data"]
    course = next((c for c in courses if c.get("id") == course_id or c.get("kode") == course_id), None)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(
                code="COURSE_NOT_FOUND",
                message=f"Mata kuliah dengan id '{course_id}' tidak ditemukan di daftar kursus aktif",
                module="elearning",
            ),
        )

    token = course.get("token_assignment")
    if not token:
        return success_response(data=summarize_grades([], []), cached=False)

    return await cached_endpoint(
        module="elearning",
        name="course_grades",
        fetch=lambda: _build_grades(nim, password, token),
        parse=lambda data: data,
        ttl=settings.TTL_GRADES,
        cache_params={"nim": nim, "course_id": course_id},
    )
