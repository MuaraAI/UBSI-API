# UBSI API Version 1.1 (Security & Remote Access) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengamankan UBSI API dengan autentikasi wajib `X-API-Key`, ekstraksi Real Client IP untuk rate limiting di balik reverse proxy/tunnel, dukungan CORS, serta menyediakan konfigurasi remote access siap pakai untuk Caddy, Nginx, dan Cloudflare Tunnel.

**Architecture:** Middleware-first security model di FastAPI. Seluruh request ke endpoint non-health (`/v1/*`, `/metrics`, dll.) divalidasi dengan `secrets.compare_digest(api_key, settings.API_KEY)`. Real Client IP diekstrak secara hierarkis (`CF-Connecting-IP` -> `X-Forwarded-For` -> `request.client.host`) agar kuota 60 req/menit bekerja per pengguna asli. Aplikasi tetap mengikat pada `127.0.0.1:8300` dan diakses dari luar melalui reverse proxy atau tunnel terisolasi.

**Tech Stack:** FastAPI, Pydantic Settings, Starlette Middleware (CORS & HTTP), Redis (aioredis), HTTPX, Pytest.

**Spec:** `docs/superpowers/specs/2026-09-25-ubsi-api-design.md` (§13 & §14).

## Global Constraints

- Backend bind address: `127.0.0.1:8300` (Localhost only, no `0.0.0.0` exposure).
- Mandatory `API_KEY` di environment produksi (Fail-fast startup jika kosong di `.env`).
- Constant-time string comparison untuk token menggunakan `secrets.compare_digest`.
- Whitelist tanpa auth hanya untuk `GET /health`.
- Seluruh 58 pengujian eksisting harus tetap 100% lulus (hijau).
- Response error auth harus menggunakan format standard envelope: `{"success": false, "error": {"code": "UNAUTHORIZED", "message": "...", "module": "auth"}}`.

## Review Focus

1. **Missing or empty `X-API-Key`**: Request ditolak dengan kode status 401 Unauthorized dan envelope error.
2. **Timing attack attempt**: Validasi key tidak menggunakan perbandingan `==` mentah.
3. **Health check bypass**: Probe `/health` tetap mengembalikan status 200 OK tanpa memerlukan header `X-API-Key`.
4. **CORS Preflight (OPTIONS)**: Request metode `OPTIONS` diizinkan langsung untuk mencegah pemblokiran oleh web browser frontend.
5. **IP collision behind reverse proxy**: Request beruntun dari IP publik berbeda di balik Cloudflare / Caddy dihitung terpisah, bukan digabung sebagai `127.0.0.1`.

---

### Task 1: Environment & Test Harness Auto-Auth (`conftest.py`)

**Files:**
- Modify: `.env.example`
- Modify: `app/config.py`
- Create: `tests/conftest.py`

**Interfaces:**
- Consumes: Pydantic BaseSettings di `app/config.py`
- Produces: `settings.API_KEY`, `settings.ALLOWED_ORIGINS`, `settings.TRUSTED_PROXIES` dan fixture autouse Pytest di `tests/conftest.py`.

- [ ] **Step 1: Write test for new config attributes in `tests/test_config.py`**

```python
def test_security_config_defaults(monkeypatch):
    from app.config import Settings
    monkeypatch.delenv("API_KEY", raising=False)
    cfg = Settings(_env_file=None)
    assert cfg.API_KEY == ""
    assert cfg.ALLOWED_ORIGINS == "*"
    assert cfg.TRUSTED_PROXIES == "127.0.0.1"
```

- [ ] **Step 2: Run test to verify failure**

Run: `.venv/bin/pytest tests/test_config.py -k test_security_config_defaults`
Expected: FAIL with AttributeError or validation error.

- [ ] **Step 3: Update `.env.example` and `app/config.py`**

Di `app/config.py`:
```python
class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8300
    REDIS_URL: str = "redis://127.0.0.1:6379/2"

    API_KEY: str = ""
    ALLOWED_ORIGINS: str = "*"
    TRUSTED_PROXIES: str = "127.0.0.1"
    ...
```

Di `.env.example`:
```bash
# SECURITY & REMOTE ACCESS
API_KEY=
ALLOWED_ORIGINS=*
TRUSTED_PROXIES=127.0.0.1
```

- [ ] **Step 4: Create `tests/conftest.py` to transparently authenticate existing test suite**

```python
import pytest
from httpx import AsyncClient
from app.config import settings

_original_init = AsyncClient.__init__

def _patched_init(self, *args, **kwargs):
    headers = kwargs.get("headers") or {}
    if "X-API-Key" not in headers:
        headers = dict(headers)
        headers["X-API-Key"] = "test-secret-key-12345"
    kwargs["headers"] = headers
    _original_init(self, *args, **kwargs)

@pytest.fixture(autouse=True)
def auto_auth_client(monkeypatch):
    monkeypatch.setattr(AsyncClient, "__init__", _patched_init)
    monkeypatch.setattr(settings, "API_KEY", "test-secret-key-12345")
```

- [ ] **Step 5: Run full pytest suite**

Run: `.venv/bin/pytest -q`
Expected: 59 passed.

- [ ] **Step 6: Commit Task 1**

```bash
git add .env.example app/config.py tests/conftest.py tests/test_config.py
git commit -m "feat(config): add API_KEY and security settings with autouse test fixture"
```

---

### Task 2: CORS & Real Client IP Extractor

**Files:**
- Modify: `app/main.py`
- Create: `tests/test_real_ip.py`

**Interfaces:**
- Consumes: `Request.headers`, `settings.ALLOWED_ORIGINS`
- Produces: `extract_client_ip(request: Request) -> str` dan integrasi ke `rate_limiting_middleware`.

- [ ] **Step 1: Write failing test in `tests/test_real_ip.py`**

```python
import pytest
from unittest.mock import MagicMock
from app.main import extract_client_ip

def test_extract_client_ip_cloudflare():
    req = MagicMock()
    req.headers = {"cf-connecting-ip": "203.0.113.195", "x-forwarded-for": "10.0.0.1"}
    req.client.host = "127.0.0.1"
    assert extract_client_ip(req) == "203.0.113.195"

def test_extract_client_ip_x_forwarded_for():
    req = MagicMock()
    req.headers = {"x-forwarded-for": "198.51.100.42, 10.0.0.1"}
    req.client.host = "127.0.0.1"
    assert extract_client_ip(req) == "198.51.100.42"

def test_extract_client_ip_fallback():
    req = MagicMock()
    req.headers = {}
    req.client.host = "127.0.0.1"
    assert extract_client_ip(req) == "127.0.0.1"
```

- [ ] **Step 2: Run test to verify failure**

Run: `.venv/bin/pytest tests/test_real_ip.py`
Expected: FAIL with `ImportError: cannot import name 'extract_client_ip'`

- [ ] **Step 3: Implement `extract_client_ip` and add CORSMiddleware in `app/main.py`**

```python
from fastapi.middleware.cors import CORSMiddleware

def extract_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"

# CORS configuration
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Update `rate_limiting_middleware` di `app/main.py`:
```python
client_ip = extract_client_ip(request)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_real_ip.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit Task 2**

```bash
git add app/main.py tests/test_real_ip.py
git commit -m "feat(security): add CORS middleware and real client IP extractor"
```

---

### Task 3: Mandatory `X-API-Key` Authentication Middleware

**Files:**
- Modify: `app/main.py`
- Create: `tests/test_auth.py`

**Interfaces:**
- Consumes: `settings.API_KEY`, `request.headers.get("x-api-key")`
- Produces: `api_key_auth_middleware` dan verifikasi startup pada `lifespan`.

- [ ] **Step 1: Write failing tests in `tests/test_auth.py`**

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check_bypasses_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={}) as ac:
        res = await ac.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_missing_api_key_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"X-API-Key": ""}) as ac:
        res = await ac.get("/v1/news")
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_invalid_api_key_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"X-API-Key": "wrong-key"}) as ac:
        res = await ac.get("/v1/news")
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"

@pytest.mark.asyncio
async def test_valid_api_key_allows_request():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"X-API-Key": "test-secret-key-12345"}) as ac:
        res = await ac.get("/metrics")
    assert res.status_code == 200
```

- [ ] **Step 2: Run test to verify failure**

Run: `.venv/bin/pytest tests/test_auth.py`
Expected: FAIL (returns 200 instead of 401 because auth middleware does not exist yet).

- [ ] **Step 3: Implement `api_key_auth_middleware` in `app/main.py`**

```python
import secrets

@app.middleware("http")
async def api_key_auth_middleware(request: Request, call_next):
    # 1. Allow CORS Preflight
    if request.method == "OPTIONS":
        return await call_next(request)

    # 2. Allow Health Check probe
    if request.url.path == "/health":
        return await call_next(request)

    # 3. Validate X-API-Key
    api_key = request.headers.get("x-api-key")
    configured_key = settings.API_KEY

    if not api_key or not configured_key or not secrets.compare_digest(api_key, configured_key):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(
                code="UNAUTHORIZED",
                message="Akses ditolak: Header X-API-Key tidak valid atau tidak disertakan",
                module="auth"
            )
        )

    return await call_next(request)
```

Tambahkan fail-fast check di `lifespan`:
```python
import os

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not settings.API_KEY and not os.getenv("PYTEST_CURRENT_TEST"):
        raise RuntimeError("API_KEY wajib disetel di file .env!")
    yield
    ...
```

- [ ] **Step 4: Run auth tests and full pytest suite**

Run: `.venv/bin/pytest tests/test_auth.py -v && .venv/bin/pytest -q`
Expected: 66 passed (58 original + 1 config + 3 real_ip + 4 auth).

- [ ] **Step 5: Commit Task 3**

```bash
git add app/main.py tests/test_auth.py
git commit -m "feat(auth): implement mandatory X-API-Key middleware and fail-fast startup"
```

---

### Task 4: Update Smoke Test CLI for API Key Support

**Files:**
- Modify: `scripts/smoke.py`

**Interfaces:**
- Consumes: Arg `--api-key` atau `os.getenv("API_KEY")` atau pembacaan `.env`.
- Produces: Live smoke test dengan header `X-API-Key` terverifikasi.

- [ ] **Step 1: Update `scripts/smoke.py`**

Tambahkan parsing argument `--api-key` dan header:
```python
parser.add_argument("--api-key", default="", help="UBSI API Key (defaults to API_KEY from .env)")
```
Di fungsi request:
```python
headers = {}
if api_key:
    headers["X-API-Key"] = api_key
```
Verifikasi `/health` dipanggil tanpa header, sedangkan endpoint lainnya menggunakan `headers`.

- [ ] **Step 2: Test `scripts/smoke.py --help`**

Run: `.venv/bin/python scripts/smoke.py --help`
Expected: Memunculkan opsi `--api-key`.

- [ ] **Step 3: Commit Task 4**

```bash
git add scripts/smoke.py
git commit -m "feat(smoke): add X-API-Key support to live smoke test CLI"
```

---

### Task 5: Production Templates & Remote Access Documentation

**Files:**
- Create: `templates/Caddyfile.example`
- Create: `templates/nginx.example.conf`
- Create: `templates/cloudflared.example.yml`
- Create: `docs/remote-access.md`
- Modify: `docs/superpowers/plans/2026-09-25-ubsi-api.md` (Update checklist)

**Interfaces:**
- Consumes: Spesifikasi Caddy, Nginx, dan Cloudflare Tunnel
- Produces: Panduan deployment remote dan template konfigurasi 1-klik copy-paste.

- [ ] **Step 1: Write `templates/Caddyfile.example`**

```caddy
api.example.com {
    # Otomatis Let's Encrypt SSL & HTTP->HTTPS redirect
    reverse_proxy localhost:8300 {
        header_up Host {upstream_hostport}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

- [ ] **Step 2: Write `templates/nginx.example.conf`**

```nginx
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8300;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- [ ] **Step 3: Write `templates/cloudflared.example.yml`**

```yaml
tunnel: <TUNNEL_UUID>
credentials-file: /home/ubuntu/.cloudflared/<TUNNEL_UUID>.json

ingress:
  - hostname: api.example.com
    service: http://127.0.0.1:8300
  - service: http_status:404
```

- [ ] **Step 4: Write `docs/remote-access.md`**

Dokumen lengkap berisi panduan setup Caddy, Nginx, dan Cloudflare Tunnel serta cara pengujian curl dengan `X-API-Key`.

- [ ] **Step 5: Commit Task 5**

```bash
git add templates/ docs/remote-access.md
git commit -m "docs(remote): add Caddy, Nginx, and Cloudflare Tunnel templates and setup guide"
```

---

### Task 6: Final Verification & VPS Deployment

**Files:**
- Modify: `README.md` (Update checklist v1.1 dan layout pohon direktori)
- Modify: `docs/architecture.md` (Update layout pohon direktori)

- [ ] **Step 1: Run full automated test suite**

Run: `.venv/bin/pytest -v`
Expected: 66 passed (100% green).

- [ ] **Step 2: Update local `.env` with a secure random `API_KEY`**

Run: Generate key with `python3 -c "import secrets; print('ubsi_sec_' + secrets.token_hex(24))"` and set in local `.env`.

- [ ] **Step 3: Update `README.md` and `docs/architecture.md`**

Centang checklist v1.1 di README dan update struktur pohon direktori (`templates/`, `docs/remote-access.md`, `tests/test_auth.py`).

- [ ] **Step 4: Commit and push changes**

```bash
git add README.md docs/architecture.md docs/superpowers/plans/2026-09-26-v1-1-security-and-remote-access.md
git commit -m "feat: complete UBSI API v1.1 security and remote access architecture"
git push origin main
```

- [ ] **Step 5: Deploy to VPS Tencent via `deploy.sh`**

Run: `./scripts/deploy.sh`
Expected: Sync files, reload PM2 `ubsi-api`, verify `/health` OK.

- [ ] **Step 6: Run live smoke test on VPS with API key**

Run: `ssh curzy-vps-tencent "API_KEY=... /home/ubuntu/.venvs/ubsi-api/bin/python /home/ubuntu/ubsi-api/scripts/smoke.py"`
Expected: 8/8 passed.

- [ ] **Step 7: Synchronize Graphify knowledge graph**

Run: `graphify update .`
Expected: AST nodes & edges fresh and synchronized.
