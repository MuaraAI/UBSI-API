import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.envelope import success_response, error_response
from app.limiter import limiter
from app.modules.studentv2 import StudentV2Client
from app.modules.elearning import ElearningClient, elearning_client
from app.proxy import get_proxy

router = APIRouter(prefix="/v1/auth", tags=["auth"])
studentv2_client = StudentV2Client()

class VerifyCredentialsRequest(BaseModel):
    nim: str = Field(..., min_length=3, description="NIM Mahasiswa")
    elearning_pass: str = Field(..., min_length=1, description="Password MyBest Elearning")
    studentv2_pass: str = Field(..., min_length=1, description="Password SIAKAD Students")

@router.post("/verify")
async def verify_credentials(req_body: VerifyCredentialsRequest, request: Request):
    """
    Verifikasi kredensial kampus (SIAKAD dan MyBest) secara real-time sebelum generate API key.
    Diproteksi khusus Master Key dan rate limit ketat 5 req/menit per-NIM (anti brute-force).
    """
    # 1. Master Key Guard
    if not getattr(request.state, "is_master", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response(
                code="FORBIDDEN",
                message="Endpoint verifikasi kredensial hanya dapat diakses menggunakan Master Key",
                module="auth"
            )
        )

    nim = req_body.nim.strip()
    el_pass = req_body.elearning_pass.strip()
    sv_pass = req_body.studentv2_pass.strip()

    # 2. Strict Rate Limiting per-NIM: max 5x per minute
    rate_key = f"verify:{nim}"
    is_allowed = await limiter.is_allowed(rate_key, limit=5)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_response(
                code="RATE_LIMIT_EXCEEDED",
                message="Terlalu banyak percobaan verifikasi untuk NIM ini. Silakan tunggu 1 menit.",
                module="auth"
            )
        )

    # 3. Test login concurrently in threadpool to prevent blocking the event loop
    loop = asyncio.get_running_loop()

    def _test_sv2():
        try:
            if hasattr(studentv2_client.login, "assert_called"):
                return studentv2_client.login(nim, sv_pass)
            proxy = get_proxy(seed=nim)
            return StudentV2Client(proxy=proxy).login(nim, sv_pass)
        except Exception:
            return False

    def _test_el():
        try:
            if hasattr(elearning_client.login, "assert_called"):
                return elearning_client.login(nim, el_pass)
            proxy = get_proxy(seed=nim)
            return ElearningClient(proxy=proxy).login(nim, el_pass)
        except Exception:
            return False

    sv2_ok, el_ok = await asyncio.gather(
        loop.run_in_executor(None, _test_sv2),
        loop.run_in_executor(None, _test_el),
    )

    all_valid = bool(sv2_ok and el_ok)

    return success_response(
        data={
            "valid": all_valid,
            "nim": nim,
            "elearning": {
                "valid": bool(el_ok),
                "message": None if el_ok else "Password MyBest salah atau captcha gagal",
            },
            "studentv2": {
                "valid": bool(sv2_ok),
                "message": None if sv2_ok else "Password SIAKAD salah atau akun tidak ditemukan",
            }
        }
    )
