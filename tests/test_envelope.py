from app.envelope import success_response, error_response

def test_success_response_default():
    data = [{"kode": "894", "nama": "DASAR PEMROGRAMAN"}]
    res = success_response(data=data)
    assert res == {
        "success": True,
        "data": data,
        "cached": False,
    }

def test_success_response_cached_and_stale():
    data = {"schedule": []}
    res = success_response(data=data, cached=True, stale=True)
    assert res == {
        "success": True,
        "data": data,
        "cached": True,
        "stale": True,
    }

def test_error_response_with_module():
    res = error_response(
        code="UPSTREAM_TIMEOUT",
        message="Layanan elibrary sedang tidak merespons",
        module="elibrary"
    )
    assert res == {
        "success": False,
        "error": {
            "code": "UPSTREAM_TIMEOUT",
            "message": "Layanan elibrary sedang tidak merespons",
            "module": "elibrary"
        }
    }

def test_error_response_without_module():
    res = error_response(
        code="INTERNAL_ERROR",
        message="Terjadi kesalahan internal"
    )
    assert res == {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Terjadi kesalahan internal"
        }
    }
