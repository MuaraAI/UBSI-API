---
name: ubsi-api
version: 1.0.0
description: Agent skill for consuming, extending, and operating the UBSI API (Unofficial BSI Campus Aggregator).
metadata:
  tags: [ubsi, api, studentv2, mybest, scraping, redis, fastapi]
---

# UBSI API Agent Skill

Use this skill when interacting with, extending, or consuming the **UBSI API** service (`127.0.0.1:8300`).

---

## 1. Quick Capabilities Overview

The UBSI API provides unified JSON endpoints for UBSI student and academic web services:

| Domain | Key Endpoints | Description |
|---|---|---|
| **System** | `GET /health` | Service and Redis connectivity healthcheck (`status: "ok"`) |
| **SIAKAD** | `GET /v1/studentv2/schedule`<br>`GET /v1/studentv2/grades`<br>`GET /v1/studentv2/announcements`<br>`GET /v1/studentv2/news` | Active course schedule, raw grades (UTS/UAS/Tugas/Grade), circulars, and archives |
| **MyBest LMS** | `GET /v1/elearning/courses`<br>`GET /v1/elearning/assignments`<br>`GET /v1/elearning/presence`<br>`GET /v1/elearning/materials`<br>`GET /v1/elearning/quiz` | Active course cards & encrypted tokens, assignment deadlines & grades, meeting attendance logs, silabus/modul ZIP links, online quizzes |
| **Library** | `GET /v1/elibrary/search?q={keyword}&opsi={buku}`<br>`GET /v1/elibrary/book/{book_id}` | OPAC book catalog search, metadata, classification, and physical shelf stock |
| **News** | `GET /v1/news?page={1}&per_page={10}&search={query}`<br>`GET /v1/news/{id}` | Official university news via native WordPress REST API |
| **Research** | `GET /v1/repository/recent`<br>`GET /v1/repository/search?q={query}`<br>`GET /v1/ejournal/journals` | EPrints publications, thesis search, and 16 official scientific journal catalog |

---

## 2. Response Standards (Clean Minimalist JSON)

All responses strictly follow the envelope format:

```json
{
  "success": true,
  "data": [...],
  "cached": false
}
```

- When upstream campus portals are experiencing downtime or maintenance, the API serves the **Last-Known-Good** snapshot marked with `"stale": true`:
  ```json
  {
    "success": true,
    "data": [...],
    "cached": true,
    "stale": true
  }
  ```
- Error format:
  ```json
  {
    "success": false,
    "error": {
      "code": "UPSTREAM_TIMEOUT",
      "message": "Deskripsi kesalahan",
      "module": "elibrary"
    }
  }
  ```

---

## 3. How to Consume in Code (Python Example)

```python
import requests

BASE_URL = "http://127.0.0.1:8300"

# 1. Fetch active schedule
res = requests.get(f"{BASE_URL}/v1/studentv2/schedule").json()
if res["success"]:
    for course in res["data"]:
        print(f"[{course['hari']} {course['jam']}] {course['nama']} - Ruang {course['ruang']} (Dosen: {course['kode_dosen']})")

# 2. Fetch LMS courses & assignments
courses_res = requests.get(f"{BASE_URL}/v1/elearning/courses").json()
if courses_res["success"]:
    first_course = courses_res["data"][0]
    token_tugas = first_course["token_assignment"]
    tasks_res = requests.get(f"{BASE_URL}/v1/elearning/assignments?token={token_tugas}").json()
    print("Tasks:", tasks_res["data"]["tasks"])
```

---

## 4. Development & Extension Rules

When adding new endpoints, modifying scrapers, or debugging:

1. **Localhost Only**: Binds strictly to `127.0.0.1:8300`. Never expose 0.0.0.0 in version 1.
2. **Scraper Engine**: Use Scrapling `FetcherSession(impersonate="chrome")` for authenticated sessions and `Fetcher.get` for public static scraping. Never run heavy headless browser bundles (e.g. Camoufox / Playwright browser downloads) on the VPS.
3. **Anti-Ban Protections**:
   - Re-use in-memory session cookies. Only trigger POST to `/login` if redirected to login.
   - Respect tiered cache TTLs: Schedule (2h), Grades (30m), Assignments (10m), News (15m), Library (1h).
   - Single-flight mutex: Serialize concurrent requests to identical uncached resources.
4. **TDD Mandatory**:
   - Save anonymized HTML snapshots into `tests/fixtures/`.
   - Unit tests must run 100% offline without live network hits to university servers (`.venv/bin/pytest -v`).

---

## 5. Operations & VPS Deployment

- **VPS Target Path**: `/home/ubuntu/ubsi-api` on `curzy-vps-tencent`.
- **Process Manager**: Managed via PM2 (`ecosystem.config.cjs`).
- **One-Command Deploy**:
  ```bash
  ./scripts/deploy.sh
  ```
- **Live Smoke Test**:
  ```bash
  .venv/bin/python scripts/smoke.py --base-url http://127.0.0.1:8300
  ```
- **PM2 Remote Management**:
  ```bash
  ssh curzy-vps-tencent "pm2 status ubsi-api"
  ssh curzy-vps-tencent "pm2 logs ubsi-api --lines 50"
  ssh curzy-vps-tencent "pm2 restart ubsi-api"
  ```
