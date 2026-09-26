# Security Policy

## 1. Scope & Intended Use

This software is an unofficial, personal automation tool designed strictly for private use by its owner to access their own academic data.

- **Localhost Core & Authenticated Ingress**: The underlying API server binds strictly to `127.0.0.1:8300` (zero open ingress ports to `0.0.0.0`). Remote access is supported exclusively through trusted reverse proxies (Caddy, Nginx) or Cloudflare Tunnel, guarded by mandatory `X-API-Key` authentication and rate limiting.
- **Single-User Ownership**: This software must only be operated with credentials belonging to the individual running the instance. Never collect, store, or process credentials belonging to third parties.

## 2. Credential Security & Privacy

- **Zero Hardcoded Secrets**: All student credentials (`STUDENTV2_NIM`, `STUDENTV2_PASS`, `ELEARNING_NIM`, `ELEARNING_PASS`) and the security access token (`API_KEY`) are loaded strictly from `.env` or system environment variables.
- **Strict File Permissions**: Production `.env` files are enforced to mode `600` (`-rw-------`), preventing read access by unauthorized system users.
- **Git Hygiene**: `.env` and local database/cache files are explicitly excluded via `.gitignore`. Never commit credentials to version control.
- **No Remote Telemetry**: This project contains no third-party tracking, analytics, or remote data exfiltration mechanisms.

## 3. Server Safety & Upstream Etika

To ensure the university's upstream infrastructure is never overloaded or disrupted:
- **Mandatory Authentication & Timing Attack Defense**: Remote endpoints require `X-API-Key` validated via `secrets.compare_digest()` in constant time.
- **Real-IP Sliding Window Rate Limiting**: Capped at 60 requests/minute per client IP (resolved via trusted proxy headers).
- **Tiered In-Memory/Redis Caching**: Prevents frequent requests to campus servers (schedules cached for 2 hours, grades for 30 minutes, tasks for 10 minutes) with Last-Known-Good offline fallback.
- **Single-Flight Mutex**: Concurrent incoming requests for the same resource never trigger parallel scrapes against university systems.
- **Human Jitter**: Paced request delays (0.8–1.5s) prevent automated burst traffic.
- **Read-Only Operation**: Version 1 restricts operations to read-only retrieval, eliminating risk of unauthorized state changes.

## 4. Reporting Vulnerabilities

If you discover a security vulnerability or sensitive information leakage within this repository, please report it directly to the maintainer via private communication rather than opening a public issue.
