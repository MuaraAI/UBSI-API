# Anti-Ban & Account Safety Protocol

This document explains the technical mechanisms implemented to ensure student campus accounts are never flagged, rate-limited, or suspended by university network monitoring systems.

---

## 1. The Core Principles

University security systems and Web Application Firewalls (WAF) monitor for abnormal traffic behavior. UBSI API mimics authentic human browsing patterns using five protective layers:

---

## 2. Protective Mechanisms

### A. In-Memory Session Cookie Re-Use
- **Problem**: Traditional automation scripts submit login credentials (POST to `/login`) on every request. Submitting 30 logins in 5 minutes is an immediate red flag.
- **Solution**: The `StudentV2Client` and `ElearningClient` maintain an in-memory session. Once authenticated, subsequent queries use the existing session cookie.
- **Auto Re-Login**: A fresh login request is dispatched **only** when the server explicitly redirects back to `/login` due to cookie expiration.

### B. Tiered Cache Expirations (TTL)
Academic data changes infrequently. Caching is tuned to the natural update cycles of each data source:

| Data Type | Cache TTL | Rationale |
|---|---|---|
| **Schedules & KRS** | 2 Hours (7200s) | Changes only at the start of a semester |
| **Semester Grades** | 30 Minutes (1800s) | Updates only during midterm/final grading periods |
| **Assignments & Quizzes** | 10 Minutes (600s) | Checked periodically during study sessions |
| **Announcements & News** | 15 Minutes (900s) | Updated several times per week |
| **Library Catalog** | 1 Hour (3600s) | Book metadata is static |

### C. Browser TLS Impersonation via Scrapling
- **Problem**: Python `requests` or `urllib` send default TLS signatures and HTTP/1.1 headers that are trivially detected and blocked by modern firewalls.
- **Solution**: Scrapling utilizes `curl_cffi` configured with `impersonate="chrome"`.
- **Result**: Cipher suites, TLS extensions, ALPN, and HTTP/2 framing match genuine Google Chrome desktop browsers identically.

### D. Single-Flight Concurrency Control
Incoming requests from multiple background worker processes for the same course or schedule are serialized through an in-memory mutex. Campus infrastructure never receives concurrent requests for the same student data.

### E. Human Pacing (Jitter)
Multi-page crawler operations introduce random delays of 0.8–1.5 seconds between requests, mirroring natural human reading speed.
