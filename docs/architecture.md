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
