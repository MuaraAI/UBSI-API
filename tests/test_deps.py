import pytest
from starlette.requests import Request
from fastapi import HTTPException
from app.config import Settings
from app.deps import require_elearning_creds, require_studentv2_creds

def test_tier1_vault_credentials():
    scope = {"type": "http", "headers": [], "state": {}}
    req = Request(scope)
    req.state.nim = "15260767"
    req.state.elearning_pass = "vault_el_pass"
    req.state.studentv2_pass = "vault_sv_pass"
    
    el_nim, el_pwd = require_elearning_creds(req)
    assert el_nim == "15260767"
    assert el_pwd == "vault_el_pass"
    
    sv_nim, sv_pwd = require_studentv2_creds(req)
    assert sv_nim == "15260767"
    assert sv_pwd == "vault_sv_pass"

def test_tier2_header_override():
    scope = {
        "type": "http",
        "headers": [
            (b"x-elearning-nim", b"15260888"),
            (b"x-elearning-pass", b"header_el_pass"),
            (b"x-studentv2-nim", b"15260999"),
            (b"x-studentv2-pass", b"header_sv_pass"),
        ],
        "state": {}
    }
    req = Request(scope)
    
    el_nim, el_pwd = require_elearning_creds(req)
    assert el_nim == "15260888"
    assert el_pwd == "header_el_pass"
    
    sv_nim, sv_pwd = require_studentv2_creds(req)
    assert sv_nim == "15260999"
    assert sv_pwd == "header_sv_pass"

def test_tier3_env_fallback():
    scope = {"type": "http", "headers": [], "state": {}}
    req = Request(scope)
    
    cfg = Settings(
        _env_file=None,
        ELEARNING_NIM="15260111",
        ELEARNING_PASS="env_el_pass",
        STUDENTV2_NIM="15260222",
        STUDENTV2_PASS="env_sv_pass"
    )
    
    el_nim, el_pwd = require_elearning_creds(req, cfg=cfg)
    assert el_nim == "15260111"
    assert el_pwd == "env_el_pass"
    
    sv_nim, sv_pwd = require_studentv2_creds(req, cfg=cfg)
    assert sv_nim == "15260222"
    assert sv_pwd == "env_sv_pass"

def test_missing_credentials_raises_400():
    scope = {"type": "http", "headers": [], "state": {}}
    req = Request(scope)
    empty_cfg = Settings(_env_file=None)
    
    with pytest.raises(HTTPException) as exc_el:
        require_elearning_creds(req, cfg=empty_cfg)
    assert exc_el.value.status_code == 400
    assert exc_el.value.detail["error"]["code"] == "CONFIG_MISSING"

    with pytest.raises(HTTPException) as exc_sv:
        require_studentv2_creds(req, cfg=empty_cfg)
    assert exc_sv.value.status_code == 400
    assert exc_sv.value.detail["error"]["code"] == "CONFIG_MISSING"

def test_backward_compatible_signature_with_settings_as_first_arg():
    empty_cfg = Settings(_env_file=None)
    with pytest.raises(HTTPException):
        require_elearning_creds(empty_cfg)
    with pytest.raises(HTTPException):
        require_studentv2_creds(empty_cfg)
