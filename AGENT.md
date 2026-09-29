# AGENT.md — AI Coding Agent Guide & Project Manual

Selamat datang di repositori **UBSI API** (`MuaraAI/UBSI-API`). Dokumen ini adalah panduan resmi operasional, arsitektur, dan konvensi kerja bagi seluruh AI Coding Agent (Hermes, Claude Code, Cursor, Codex, Copilot, dll.) dan pengembang yang berkontribusi pada proyek ini.

---

## 1. Project Overview & Authors

* **Nama Proyek:** UBSI API
* **Deskripsi:** Unofficial REST API Aggregator untuk 6 layanan kampus Universitas Bina Sarana Informatika (SIAKAD, Elearning MyBest, Perpustakaan, Berita Resmi, Repository EPrints, dan E-Journal OJS).
* **Repositori Resmi:** [https://github.com/MuaraAI/UBSI-API](https://github.com/MuaraAI/UBSI-API) (Organisasi: `MuaraAI`, Public)
* **Lisensi:** MIT License
* **Core Team & Maintainers:**
  - **Yuken Velino** ([@Curzyori](https://github.com/Curzyori)) — Lead Developer & Creator (Informatika, FTI UBSI)
  - **Verzio** ([@MyKineID](https://github.com/MyKineID)) — Core Contributor (Informatika, FTI UBSI)
  - **Muhammad Raffli Aldiansyah** ([@Seeyaa77](https://github.com/Seeyaa77)) — Core Contributor (Informatika, FTI UBSI)

---

## 2. Monorepo Architecture & Codebase Map

Proyek ini menggunakan arsitektur monorepo dengan pemisahan tegas antara backend Python dan frontend Next.js:

```text
UBSI-API/
├── app/                       # [BACKEND] Core FastAPI Application (Python 3.12+)
│   ├── config.py              # Pydantic BaseSettings, manajemen environment, TTL cache
│   ├── cache.py               # Redis Two-Tier Cache (Fresh + Last-Known-Good SWR)
│   ├── session_pool.py        # Multi-tenant SessionPool per-NIM (5-min idle eviction)
│   ├── limiter.py             # Sliding-window rate limiter (60 req/menit per client IP)
│   ├── deps.py                # Credential dependency injection (Header > .env fallback)
│   ├── envelope.py            # Standard clean JSON envelope format
│   ├── router_helper.py       # Helper cached_endpoint (caching, single-flight mutex, SWR)
│   ├── retry.py               # Exponential backoff scraper retry dengan jitter
│   ├── main.py                # Server entrypoint, middleware auth & proxy, health, metrics
│   └── modules/               # Scraper & Parser tiap domain kampus
│       ├── studentv2.py       # SIAKAD (students.bsi.ac.id): Jadwal, Nilai, Berita, Dashboard
│       ├── elearning.py       # MyBest (elearning.bsi.ac.id): Matkul, Tugas, Presensi, Modul, Kuis
│       ├── elibrary.py        # Perpustakaan (elibrary.bsi.ac.id): OPAC search, stok buku
│       ├── news.py            # Portal Berita (news.bsi.ac.id) & Multi-Channel Webhook Broadcaster
│       ├── repository.py      # EPrints Publikasi (repository.bsi.ac.id): Riset & skripsi terbaru
│       └── ejournal.py        # E-Journal (ejournal.bsi.ac.id): 23 jurnal aktif via OAI bypass
│
├── web/                       # [FRONTEND] Landing Page & Documentation (Next.js 15)
│   ├── src/app/               # App Router, layout, globals.css, open-graph image, SEO
│   ├── src/components/        # Komponen UI Deep Water (Navbar, Hero, CodeShowcase, dll.)
│   ├── src/data/              # Dataset statis modul kampus, kontributor, dan contoh payload
│   ├── public/fonts/          # Self-hosted woff2 Google Fonts (Space Grotesk, Inter, JetBrains Mono)
│   └── DESIGN.md              # Token desain resmi Deep Water (navy, teal, dark-first)
│
├── tests/                     # [TEST SUITE] Pytest 100% Offline (78+ Passing Tests)
│   ├── fixtures/              # Snapshot HTML statis kampus (sv2_*.html, el_*.html)
│   ├── test_studentv2_*.py    # Parser & router tests untuk SIAKAD
│   ├── test_elearning_*.py    # Parser & router tests untuk MyBest
│   ├── test_elibrary_*.py     # Parser & router tests untuk perpustakaan
│   ├── test_public_*.py       # Parser & router tests untuk News, Repo, E-Journal
│   └── test_integration.py    # Pipeline integration test
│
├── docs/                      # Dokumentasi teknis, arsitektur, anti-ban, dan deploy
├── skills/                    # Agent skills & workflows lokal (SKILL.md)
└── .gitignore                 # Exclusion rules (.env, data/, anti-slop/, graphify-out/)
```

---

## 3. Git Workflow & Contribution Rules (WAJIB DIIKUTI AGENT)

Dilarang keras melakukan direct commit dan direct push ke branch `main`! Setiap agen wajib mengikuti salah satu dari dua alur di bawah:

### Alur A: Anggota Tim / Internal Komunitas (Akses Push Langsung)
1. **Buat Feature Branch Baru:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b <type>/<deskripsi-singkat>
   # Contoh: feat/ical-calendar, fix/captcha-solver, docs/api-update
   ```
2. **Kembangkan Fitur & Lakukan Pengujian Lokal:**
   Pastikan seluruh test lokal lulus tanpa error.
3. **Commit dengan Format Conventional Commits:**
   ```bash
   git add <file-terkait>
   git commit -m "<type>(<scope>): <pesan jelas dan ringkas>"
   # Contoh: feat(elearning): add endpoint for quiz submission list
   ```
4. **Push Branch ke Remote Repo:**
   ```bash
   git push -u origin <nama-branch>
   ```
5. **Buat Pull Request (PR) ke `main`:**
   Gunakan GitHub CLI (`gh pr create`) atau web GitHub untuk membuka PR, sertakan ringkasan perubahan dan bukti pengujian. Tunggu review/konfirmasi sebelum merge.

### Alur B: Kontributor Eksternal (Open Source)
1. **Fork Repositori:** Fork `MuaraAI/UBSI-API` ke akun personal GitHub kontributor.
2. **Kembangkan di Branch Fork:** Kerjakan perubahan pada branch di repositori fork.
3. **Buka Cross-Repo Pull Request:** Buat PR dari branch fork ke `MuaraAI/UBSI-API:main`.

---

## 4. Aturan Ketat untuk AI Agent (Iron Rules)

### 1. Zero Secrets Rule (Keamanan Kredensial)
* Jangan pernah membaca, mencetak ke chat, meng-hardcode, atau men-stage kredensial/token/password ke dalam git.
* Semua rahasia (`API_KEY`, `STUDENTV2_NIM`, `STUDENTV2_PASS`, `ELEARNING_PASSWORD`, dll.) hanya boleh dibaca dari file `.env` lokal (terdaftar di `.gitignore`).
* Dilarang menambahkan hardcoded fallback pada environment variable (misal: `os.getenv("KEY", "default_secret")`).

### 2. Strict Offline TDD (Dilarang Live Hit di Test Suite)
* Seluruh unit dan integration test di `tests/` **HARUS 100% OFFLINE**.
* Dilarang mengirim request HTTP langsung ke server kampus BSI (`*.bsi.ac.id`) di dalam test suite pytest.
* Setiap parser baru atau perbaikan parser wajib menggunakan file snapshot HTML statis di `tests/fixtures/`.

### 3. Anti-Slop & Frontend Design Standards (Direktori `/web`)
* **Zero Em-Dash:** Dilarang menggunakan karakter em dash (`—`) pada copy/metadata antarmuka; gunakan titik dua (`:`) atau titik (`.`).
* **Zero CDN Fonts:** Semua font wajib self-hosted `.woff2` di `web/public/fonts/`. Dilarang menggunakan `<link>` Google Fonts eksternal.
* **Zero Decorative Emojis:** Dilarang menggunakan emoji sebagai ikon UI atau dekorasi; gunakan ikon SVG atau Material glyphs.
* **Mobile Floor 360px:** Seluruh tampilan antarmuka wajib responsif dan bebas overflow horizontal (`scrollWidth <= clientWidth`) hingga lebar layar minimum 360px.
* **Aksesibilitas (WCAG AAA):** Rasio kontras teks utama minimal 7:1 (saat ini Deep Water mencapai 15.8:1), tombol drawer mobile wajib merespons tombol keyboard `Escape`, dan sertakan skip-link ke `#main-content`.

### 4. Verification Gate Before Claiming Completion
Sebelum menyatakan tugas selesai, agen **WAJIB** menjalankan pengujian nyata:
1. **Backend Tests:**
   ```bash
   .venv/bin/pytest -q
   # Wajib 100% lulus (minimal 71 passed)
   ```
2. **Frontend Build Check (jika memodifikasi `/web`):**
   ```bash
   cd web && npm run build
   # Wajib compiled successfully tanpa type error
   ```
3. **Knowledge Graph Sync:**
   ```bash
   graphify update .
   ```

---

## 5. Cheatsheet Perintah Pengembangan

### Menyiapkan Environment Lokal (Python)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Menjalankan Backend FastAPI (Localhost Port 8300)
```bash
uvicorn app.main:app --port 8300 --reload
# Dokumentasi Swagger UI: http://127.0.0.1:8300/docs
```

### Menjalankan Frontend Next.js 15
```bash
cd web
npm install
npm run dev
# Buka di browser: http://localhost:3000
```

### Menjalankan Smoke Test Lengkap
```bash
.venv/bin/python scripts/smoke.py --base-url http://127.0.0.1:8300
```

---

*Disusun dengan disiplin tinggi oleh Muara AI. Setiap agen yang bekerja di repo ini diharapkan menjunjung tinggi integritas kode, kebersihan git history, dan etika keamanan data kampus.*
