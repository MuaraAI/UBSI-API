# Architecture

UBSI API is structured as a single-process FastAPI application designed for high resilience, low memory footprint (~60–80 MB RAM), and non-invasive upstream querying.

---

## 1. Request Lifecycle

```text
Client Request
      │
      ▼
┌──────────────────────────────────────────────┐
│ Rate Limiter (Redis Sliding Window)          │
│ • Max 60 requests/minute per client IP       │
│ • Fail-open: Passes requests if Redis down   │
└──────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────┐
│ Route Handler & Input Validation             │
│ • Modular Credential Check (Option B)        │
└──────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────┐
│ Cache Manager (Redis DB 2)                   │
│                                              │
│ [1] Check Fresh Cache (TTL 10m - 2h)         │
│     ├── HIT  ──► Return {"cached": true}     │
│     └── MISS ──► Acquire Single-Flight Mutex │
└──────────────────────────────────────────────┘
      │ (Lock Acquired)
      ▼
┌──────────────────────────────────────────────┐
│ Scrapling Client Module                      │
│ • Re-use in-memory session cookie            │
│ • Chrome desktop TLS fingerprint (curl_cffi) │
│ • Auto-detect /login redirect & re-login 1x  │
│ • Pure HTML/JSON Parser                      │
└──────────────────────────────────────────────┘
      │
      ├── SUCCESS ──► Save to Redis:
      │               • Fresh Cache (with TTL)
      │               • Last-Known-Good (no TTL)
      │               Return {"cached": false}
      │
      └── UPSTREAM FAILURE ──► Read Last-Known-Good:
                               ├── LGG Found ──► Return {"cached": true, "stale": true}
                               └── No LGG    ──► Return 502 Bad Gateway
```

---

## 2. Two-Tier Caching Strategy

Scraping university websites is inherently susceptible to server timeouts, seasonal maintenance, and maintenance down-times. UBSI API mitigates this using a **two-tier cache**:

1. **Fresh Cache (`{key}:fresh`)**:
   - Stored with an explicit expiration (TTL).
   - Serves immediate responses without touching university servers.
2. **Last-Known-Good Cache (`{key}:lgg`)**:
   - Stored without an expiration date.
   - Updates every time a successful fetch occurs.
   - Acts as a safety net: if campus servers time out or fail, the API serves the most recent valid payload marked with `"stale": true` instead of failing with 500/502.

---

## 3. Single-Flight Mutex

To prevent the "thundering herd" problem where multiple simultaneous requests hit university servers at once:
- Each unique cache key possesses an in-process `asyncio.Lock()`.
- The first request executes the network scrape.
- Subsequent requests wait for the lock to release and consume the newly cached data.
- University servers receive at most **1 concurrent request** per resource.

---

## 4. Key Hashing Algorithm

All cache keys are generated deterministically using SHA-256 truncation:
```python
key_hash = hashlib.sha256(f"{module}:{path}:{sorted_params}".encode()).hexdigest()[:16]
full_key = f"ubsi:{module}:{key_hash}"
```
This isolates cache namespaces across modules and query parameters.

---

## 5. Session Pool & Parallel Aggregation

### A. Per-NIM Session Isolation (`app/session_pool.py`)
To prevent concurrent requests from different student credentials from overwriting each other's session cookies:
- The scraper client wraps instances inside `SessionPool`.
- Each unique NIM maintains its own independent authenticated HTTP client.
- Idle sessions are automatically evicted after 15 minutes (`ttl_seconds=900`) to conserve VPS RAM.
- Expired sessions trigger immediate invalidation so subsequent calls trigger a clean re-login.

### B. Parallel Dashboard Endpoint (`/v1/studentv2/dashboard`)
Retrieves 4 critical academic sections (`schedule`, `grades`, `news`, `announcements`) concurrently using `asyncio.gather(..., return_exceptions=True)`:
- Total response latency equals the single slowest upstream section rather than the sum of all 4.
- Sections with valid cached payloads are served immediately without hitting upstream servers.
- A failure in one section (e.g. news maintenance) is isolated and does not fail the remaining sections.

---

## 6. Multi-Channel Webhook Broadcaster (`app/modules/news.py`)

UBSI API includes an automated background watcher for new campus publications:
- **Background Worker (`lifespan`)**: Non-blocking async loop checking upstream WordPress REST API every 10 minutes (`NEWS_WEBHOOK_INTERVAL`).
- **Cold-Start Protection**: First run seeds current post IDs into Redis (`ubsi:news:seen_ids`, TTL 30 days) to prevent spamming notifications on reboot.
- **Parallel Multi-Channel Delivery**:
  - **Discord Webhook**: Rich Embeds formatted with Teal (`#2DD4BF`), article banner image, and clickable links.
  - **Telegram Bot API**: HTML-escaped messages sent via `sendPhoto` with automatic fallback to `sendMessage`.
  - **Custom Webhook**: Generic JSON payload `{"event": "news.published", "data": {...}}`.
- **Fault-Tolerant & Retry**: Dispatches via `asyncio.gather(*tasks, return_exceptions=True)`. Posts are only marked as seen if delivery succeeds, retrying automatically on the next cycle if upstream or network fails.

---

## 7. Repository Layout

```text
UBSI-API/
├── app/
│   ├── modules/
│   │   ├── studentv2.py       # SIAKAD: Jadwal, Nilai, Berita, Pengumuman, Dashboard
│   │   ├── elearning.py       # MyBest: Captcha solver, Courses, Absensi, Tugas, Materi, Kuis
│   │   ├── elibrary.py        # Perpus: OPAC search, Book detail, 60s retry
│   │   ├── news.py            # Portal: Native WP REST API & Multi-channel Webhook
│   │   ├── repository.py      # EPrints: Recent publications & search
│   │   └── ejournal.py        # OJS: 23 Journal catalog with real titles
│   ├── cache.py               # Redis 2-tier cache (fresh + LGG) & single-flight mutex
│   ├── config.py              # Pydantic Settings & tiered TTLs
│   ├── deps.py                # Modular credential validation (Option B)
│   ├── envelope.py            # Clean Minimalist JSON envelope
│   ├── limiter.py             # Sliding window rate limiter (60 req/min)
│   ├── retry.py               # Exponential backoff retry with jitter
│   ├── router_helper.py       # Helper generik cache, lock, & SWR
│   ├── session_pool.py        # Pool sesi per-NIM dengan idle TTL (15m)
│   └── main.py                # Base FastAPI app & global middleware
├── tests/
│   ├── fixtures/              # Snapshot HTML offline (sv2_*.html, el_*.html)
│   ├── conftest.py            # Fixture autouse & test auth client
│   └── test_*.py              # 78 Automated unit & integration tests
├── templates/
│   ├── Caddyfile.example      # Caddy reverse proxy template (HTTPS auto)
│   ├── nginx.example.conf     # Nginx reverse proxy configuration template
│   └── cloudflared.example.yml# Cloudflare Tunnel ingress template
├── scripts/
│   ├── deploy.sh              # 1-klik deploy ke VPS Tencent via rsync & PM2
│   └── smoke.py               # Live verification CLI tool (8 checks, auth-aware)
├── skills/
│   └── SKILL.md               # Agent skill definition for AI assistants
├── docs/
│   ├── api.md                 # 20 Endpoints dictionary & JSON payloads
│   ├── architecture.md        # Request lifecycle, session pool, and cache flow
│   ├── anti-ban.md            # Account security & safety protocols
│   ├── deploy.md              # VPS PM2 production operations
│   └── remote-access.md       # Caddy, Nginx, & Cloudflare Tunnel guide
├── ecosystem.config.cjs       # PM2 production config untuk VPS
├── CONTRIBUTING.md            # Panduan kontribusi & layout tests
├── SECURITY.md                # Kebijakan etika & privasi akademik
├── DMCA.md                    # Kebijakan hak cipta & takedown notice
├── LICENSE                    # MIT License (c) 2026 Yuken Velino
└── requirements.txt           # Project dependencies
```
