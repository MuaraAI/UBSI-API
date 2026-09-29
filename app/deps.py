from typing import Optional
from fastapi import Request, HTTPException, status
from app.config import Settings, settings
from app.envelope import error_response

def require_studentv2_creds(
    request: Request = None,  # type: ignore[assignment]
    cfg: Settings = settings
) -> tuple[str, str]:
    # Support direct/legacy test call: require_studentv2_creds(empty_settings)
    if isinstance(request, Settings):
        cfg = request
        request = None

    # Tier 1: Member Vault (injected by api_key_auth_middleware into request.state)
    if request is not None and hasattr(request, "state"):
        nim = getattr(request.state, "nim", None)
        pwd = getattr(request.state, "studentv2_pass", None)
        if nim and pwd:
            return str(nim), str(pwd)

    # Tier 2: Manual Developer Header Override
    if request is not None and hasattr(request, "headers"):
        h_nim = request.headers.get("x-studentv2-nim") or request.headers.get("x-nim")
        h_pass = request.headers.get("x-studentv2-pass") or request.headers.get("x-pass")
        if h_nim and h_pass:
            return h_nim.strip(), h_pass.strip()

    # Tier 3: Local .env Fallback (Standalone / Single-User mode)
    if cfg.STUDENTV2_NIM and cfg.STUDENTV2_PASS:
        return cfg.STUDENTV2_NIM, cfg.STUDENTV2_PASS

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=error_response(
            code="CONFIG_MISSING",
            message="Kredensial SIAKAD belum diatur (daftarkan API key atau atur STUDENTV2_NIM dan STUDENTV2_PASS di .env)",
            module="studentv2"
        )
    )

def require_elearning_creds(
    request: Request = None,  # type: ignore[assignment]
    cfg: Settings = settings
) -> tuple[str, str]:
    # Support direct/legacy test call: require_elearning_creds(empty_settings)
    if isinstance(request, Settings):
        cfg = request
        request = None

    # Tier 1: Member Vault (injected by api_key_auth_middleware into request.state)
    if request is not None and hasattr(request, "state"):
        nim = getattr(request.state, "nim", None)
        pwd = getattr(request.state, "elearning_pass", None)
        if nim and pwd:
            return str(nim), str(pwd)

    # Tier 2: Manual Developer Header Override
    if request is not None and hasattr(request, "headers"):
        h_nim = request.headers.get("x-elearning-nim") or request.headers.get("x-nim")
        h_pass = request.headers.get("x-elearning-pass") or request.headers.get("x-pass")
        if h_nim and h_pass:
            return h_nim.strip(), h_pass.strip()

    # Tier 3: Local .env Fallback (Standalone / Single-User mode)
    if cfg.ELEARNING_NIM and cfg.ELEARNING_PASS:
        return cfg.ELEARNING_NIM, cfg.ELEARNING_PASS

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=error_response(
            code="CONFIG_MISSING",
            message="Kredensial Elearning belum diatur (daftarkan API key atau atur ELEARNING_NIM dan ELEARNING_PASS di .env)",
            module="elearning"
        )
    )
