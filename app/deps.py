from fastapi import HTTPException, status
from app.config import Settings, settings
from app.envelope import error_response

def require_studentv2_creds(cfg: Settings = settings) -> tuple[str, str]:
    if not cfg.STUDENTV2_NIM or not cfg.STUDENTV2_PASS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                code="CONFIG_MISSING",
                message="STUDENTV2_NIM dan STUDENTV2_PASS belum diatur di .env",
                module="studentv2"
            )
        )
    return cfg.STUDENTV2_NIM, cfg.STUDENTV2_PASS

def require_elearning_creds(cfg: Settings = settings) -> tuple[str, str]:
    if not cfg.ELEARNING_NIM or not cfg.ELEARNING_PASS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                code="CONFIG_MISSING",
                message="ELEARNING_NIM dan ELEARNING_PASS belum diatur di .env",
                module="elearning"
            )
        )
    return cfg.ELEARNING_NIM, cfg.ELEARNING_PASS
