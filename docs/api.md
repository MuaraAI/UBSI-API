# API Reference

UBSI API organizes all endpoints under the `/v1/` prefix. Every endpoint returns a standardized Clean Minimalist JSON envelope.

---

## Response Envelope Format

### Successful Response (`200 OK`)
```json
{
  "success": true,
  "data": [...],
  "cached": false
}
```
*Note: When served from the Last-Known-Good fallback cache during upstream outages, an additional field `"stale": true` is included.*

### Error Response (`4xx` / `5xx`)
```json
{
  "success": false,
  "error": {
    "code": "UPSTREAM_TIMEOUT",
    "message": "Deskripsi kesalahan teknis",
    "module": "elibrary"
  }
}
```

---

## Authentication & Dual-Mode Access

UBSI API supports two operating modes:

### 1. Standalone / Self-Host Mode (Default)
Run locally or on your own VPS with a single master key:
- Header: `X-API-Key: <your_configured_API_KEY>`
- Campus credentials default to `.env` (`STUDENTV2_NIM`, `STUDENTV2_PASS`, `ELEARNING_NIM`, `ELEARNING_PASS`).
- Developer overrides supported per-request via headers: `X-Studentv2-NIM`, `X-Studentv2-Pass`, `X-Elearning-NIM`, `X-Elearning-Pass`.
- Rate limiting: Unlimited for Master Key.

### 2. Cloud Hosted Mode (Muara AI Platform)
Deployed on `api.muaraai.com` or `ubsi-api.muaraai.com` with multi-tenancy:
- Header: `X-API-Key: muara_live_<member_key>`
- The backend automatically resolves and decrypts (AES-256-GCM) the student's bound NIM and campus passwords from the Supabase Vault with zero DB latency (Redis cached for 10 minutes).
- Rate limiting: 60 requests/minute per member key (sliding-window).

### API Gateway Prefix (`ROOT_PATH`)
When proxied behind an API Gateway (e.g., Caddy handling `api.muaraai.com/v1/ubsi-api/*`), set `ROOT_PATH=/v1/ubsi-api` in `.env`. Swagger UI (`/docs`) and OpenAPI schema automatically adjust to the sub-path prefix.

### `POST /v1/auth/verify`
Pre-validation endpoint used by community portal (`muaraai.com`) to verify that student credentials actually authenticate against both campus portals (`students.bsi.ac.id` and `elearning.bsi.ac.id`) before persisting them into the encrypted vault.
- **Access**: Master Key Only (`request.state.is_master == True`). Member keys return `403 FORBIDDEN`.
- **Rate Limit**: Max 5 requests/minute per NIM (sliding-window anti-brute-force protection).
- **Request Body**:
  ```json
  {
    "nim": "15260767",
    "elearning_pass": "mybest_password",
    "studentv2_pass": "siakad_password"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "valid": true,
      "nim": "15260767",
      "elearning": { "valid": true, "message": null },
      "studentv2": { "valid": true, "message": null }
    }
  }
  ```

---

## 1. System

### `GET /health`
Returns runtime status and Redis connectivity.
- **Access**: Public
- **Response**:
  ```json
  {
    "status": "ok",
    "redis": "up"
  }
  ```

### `GET /metrics`
Returns operational metrics regarding active login session pools and cache status.
- **Access**: Public
- **Response**:
  ```json
  {
    "status": "ok",
    "redis": "up",
    "active_sessions": 2,
    "studentv2_sessions": 1,
    "elearning_sessions": 1,
    "uptime_note": "sessions are per-NIM with 15 min idle TTL"
  }
  ```

---

## 2. StudentV2 (SIAKAD)

All StudentV2 endpoints require `STUDENTV2_NIM` and `STUDENTV2_PASS` configured in `.env`.

### `GET /v1/studentv2/dashboard`
Retrieves course schedule, raw grades, news, and circular announcements in parallel within a single request.
- **Cache**: Re-uses existing fresh cache per section; section failure does not break the entire response.
- **Response Sample**:
  ```json
  {
    "success": true,
    "data": {
      "schedule": [...],
      "grades": [...],
      "news": [...],
      "announcements": [...]
    },
    "cached": false
  }
  ```

### `GET /v1/studentv2/schedule`
Retrieves the official course schedule for the active semester.
- **Cache TTL**: 2 hours (7200 seconds)
- **Response Sample**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "e0a17f300c3b",
        "kode": "104",
        "nama": "BAHASA INGGRIS I",
        "hari": "Selasa",
        "jam": "09:10-10:50",
        "sks": 2,
        "kelompok_praktek": null,
        "ruang": "EN2-P1",
        "kode_dosen": "TDL"
      }
    ],
    "cached": false
  }
  ```

### `GET /v1/studentv2/grades`
Retrieves raw semester grades including UTS, UAS, assignments, attendance, total score, and final letter grade.
- **Cache TTL**: 30 minutes (1800 seconds)
- **Response Sample**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "c104",
        "kode": "104",
        "nama": "BAHASA INGGRIS I",
        "sks": 2,
        "uts": 85.0,
        "uas": 90.0,
        "tugas": 88.0,
        "absen": 100.0,
        "total": 89.5,
        "grade": "A"
      }
    ],
    "cached": false
  }
  ```

### `GET /v1/studentv2/news`
Archives of official student circulars and news announcements.
- **Parameters**: `limit` (default: 50, max: 200)
- **Cache TTL**: 15 minutes (900 seconds)

### `GET /v1/studentv2/announcements`
Latest internal announcements and PDF notices displayed on the student portal dashboard.
- **Cache TTL**: 15 minutes (900 seconds)

---

## 3. Elearning (MyBest LMS)

All Elearning endpoints require `ELEARNING_NIM` and `ELEARNING_PASS` configured in `.env`.

### `GET /v1/elearning/courses`
Lists enrolled LMS courses with schedule metadata and encrypted action tokens.
- **Cache TTL**: 10 minutes (600 seconds)
- **Response Sample**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "c101",
        "kode": "101",
        "nama": "PENDIDIKAN PANCASILA",
        "sks": 2,
        "kode_dosen": "BDM",
        "kelompok_praktek": null,
        "kode_gabung": "KG.101.30.C",
        "jadwal": {
          "hari": "Jumat",
          "jam": "07:30-09:10",
          "ruang": "EL2-P1"
        },
        "tokens": {
          "absen": "eyJpdi...",
          "diskusi": "eyJpdi...",
          "learning": "eyJpdi...",
          "assignment": "eyJpdi..."
        },
        "token_absen": "eyJpdi...",
        "token_assignment": "eyJpdi...",
        "token_learning": "eyJpdi...",
        "token_diskusi": "eyJpdi..."
      }
    ],
    "cached": false
  }
  ```

### `GET /v1/elearning/assignments`
Retrieves active assignment requirements, deadlines, and graded submission history.
- **Query Parameter**: `token` (optional; when omitted, aggregates all active assignments across all courses)
- **Cache TTL**: 10 minutes (600 seconds)

### `GET /v1/elearning/presence`
Retrieves lecture attendance status, classroom/session header information, and meeting history.
- **Query Parameter**: `token` (optional)
- **Cache TTL**: 10 minutes (600 seconds)
- **Response Sample**:
  ```json
  {
    "success": true,
    "data": {
      "kode_mtk": "101",
      "matakuliah": "PENDIDIKAN PANCASILA",
      "kelas": "KG.101.30.C",
      "dosen": "BDM",
      "ruang": "EL2-P1",
      "hari": "Jumat",
      "jam_masuk": "07:30",
      "jam_keluar": "09:10",
      "status_sesi": "Sudah Selesai",
      "total_kehadiran": 0,
      "riwayat": []
    },
    "cached": false
  }
  ```

### `GET /v1/elearning/materials`
Retrieves direct download links for lecture syllabus and weekly module packages (ZIP/PDF).
- **Query Parameter**: `token` (optional)
- **Cache TTL**: 10 minutes (600 seconds)

### `GET /v1/elearning/quiz`
Retrieves active online quizzes and practice exam schedules.
- **Cache TTL**: 10 minutes (600 seconds)

### `GET /v1/elearning/grades`
Recap of assignment grades (and quiz schedules) per meeting across all active
courses, or a single course when the optional `token` query parameter (from
`/v1/elearning/courses`) is provided. Returns totals, graded/ungraded counts,
average/max/min scores, per-course breakdown, and per-meeting rows.
- **Query Parameter**: `token` (optional)
- **Cache TTL**: 30 minutes (1800 seconds)

### `GET /v1/elearning/courses/{course_id}/grades`
Same recap scoped to one course. `course_id` accepts either the 12-char hex `id` or the course code (`kode`, e.g. `104` or `101`) from `GET /v1/elearning/courses`. Returns `404 COURSE_NOT_FOUND` when the course is unknown.
- **Cache TTL**: 30 minutes (1800 seconds)

---

## 4. Elibrary (Library Catalog)

Public catalog search and physical book availability.

### `GET /v1/elibrary/search`
Searches the OPAC public catalog.
- **Query Parameters**:
  - `q` (required): Search keyword.
  - `opsi` (default: `buku`): Options include `buku`, `semua`, `ta`, `skripsi`, `jurnal`, `prosiding`, `ebook`.
  - `page` (default: 1): Page offset number.
- **Cache TTL**: 1 hour (3600 seconds)
- **Response Sample**:
  ```json
  {
    "success": true,
    "data": {
      "total_count": 967,
      "items": [
        {
          "id": "240688",
          "title": "Kupas tuntas algoritma clustering",
          "url": "https://elibrary.bsi.ac.id/readbook/240688/kupas-tuntas-algoritma-clustering"
        }
      ]
    },
    "cached": false
  }
  ```

### `GET /v1/elibrary/book/{book_id}`
Retrieves book metadata, classification code, publisher, ISBN, and physical shelf stock.
- **Cache TTL**: 1 hour (3600 seconds)

---

## 5. News & Publications

Public institutional news and scientific publications.

### `GET /v1/news`
Fetches official news posts directly from the WordPress REST API (`news.bsi.ac.id`).
- **Query Parameters**:
  - `search` (optional): Filter articles by keyword.
  - `page` (default: 1): Pagination page number.
  - `per_page` (default: 10, max: 50): Articles per page.
- **Cache TTL**: 15 minutes (900 seconds)

### `GET /v1/news/{post_id}`
Retrieves full rendered HTML content and author metadata for a specific article.

### `POST /v1/news/webhook/test`
Sends a test news publication alert to configured channels (`all`, `discord`, `telegram`, or `custom`) or explicit target parameters.
- **Query Parameters**:
  - `channel` (optional, default: `all`): Target channel to test (`all`, `discord`, `telegram`, `custom`).
  - `target_url` (optional): Override webhook URL for testing ad-hoc endpoints (Discord / Custom).
  - `telegram_bot_token` (optional): Override Telegram bot token for testing.
  - `telegram_chat_id` (optional): Override Telegram target chat ID for testing.
- **Requires Auth**: Yes (`X-API-Key`)
- **Sample Response**:
  ```json
  {
    "success": true,
    "data": {
      "message": "Pengujian broadcast channel 'all' selesai",
      "results": {
        "discord": { "configured": true, "success": true, "target": "https://discord.com/api/webhooks/..." },
        "telegram": { "configured": true, "success": true, "chat_id": "@channel_kampus" },
        "custom": { "configured": true, "success": true, "target": "https://bot-ciel.internal/api/webhook" }
      }
    },
    "cached": false
  }
  ```

### `GET /v1/repository/recent`
Retrieves recent undergraduate theses and faculty research publications from EPrints.
- **Cache TTL**: 1 hour (3600 seconds)

### `GET /v1/repository/search?q={query}`
Performs a full-text search across institutional research publications.

### `GET /v1/ejournal/journals`
Lists the catalog of 23 official UBSI peer-reviewed scientific journals.
- **Cache TTL**: 1 hour (3600 seconds)
