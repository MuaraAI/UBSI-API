from typing import Any, Optional

def success_response(
    data: Any,
    cached: bool = False,
    stale: bool = False
) -> dict[str, Any]:
    res: dict[str, Any] = {
        "success": True,
        "data": data,
        "cached": cached,
    }
    if stale:
        res["stale"] = True
    return res

def error_response(
    code: str,
    message: str,
    module: Optional[str] = None
) -> dict[str, Any]:
    err_obj: dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if module:
        err_obj["module"] = module
    return {
        "success": False,
        "error": err_obj,
    }
