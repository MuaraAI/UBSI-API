<h1 align="center">UBSI API</h1>
<p align="center">
  <strong>Unofficial REST API Aggregator for 6 UBSI University Services</strong>
</p>

<p align="center">
  Unified JSON interface for StudentV2 (SIAKAD), MyBest LMS, Elibrary, EJournal, Repository, and News Portal.
</p>

<div align="center">

  <a href="https://ubsi-api.muaraai.com"><img src="https://img.shields.io/badge/website-ubsi--api.muaraai.com-2DD4BF?style=for-the-badge&logo=vercel&logoColor=white" alt="Website" /></a>
  <a href="https://github.com/MuaraAI/UBSI-API"><img src="https://img.shields.io/badge/status-active-success?style=for-the-badge&color=374151" alt="Status" /></a>
  <a href="https://github.com/MuaraAI/UBSI-API/blob/main/LICENSE"><img src="https://img.shields.io/github/license/MuaraAI/UBSI-API?style=for-the-badge&color=374151" alt="License" /></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&color=374151" alt="Python Version" />
  <img src="https://img.shields.io/badge/next.js-15-black?style=for-the-badge&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/cache-Redis%20DB2-red?style=for-the-badge&color=374151" alt="Redis Cache" />

</div>

<p align="center">
  <a href="#disclaimer">Disclaimer</a> ·
  <a href="#why">Why</a> ·
  <a href="#key-features">Features</a> ·
  <a href="#endpoints">Endpoints</a> ·
  <a href="#tech-stack">Tech Stack</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#testing">Testing</a> ·
  <a href="#deployment">Deployment</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#contributors">Contributors</a> ·
  <a href="#roadmap">Roadmap</a> ·
  <a href="#license">License</a>
</p>

---

## <a id="disclaimer"></a>⚠️ PENTING / DISCLAIMER RESMI

> **Pernyataan Penafian (Disclaimer)**:
> 
> Proyek **UBSI API** adalah *unofficial software* (perangkat lunak tidak resmi) yang dikembangkan secara independen oleh mahasiswa **Universitas Bina Sarana Informatika (UBSI)** untuk keperluan riset rekayasa perangkat lunak, otomatisasi personal, dan efisiensi waktu dalam mengakses jadwal, tugas, nilai, serta materi perkuliahan tanpa navigasi manual berulang.
>
> 1. Proyek ini **tidak berafiliasi resmi, tidak disponsori, dan tidak dikelola oleh pihak Universitas Bina Sarana Informatika (UBSI)**.
> 2. Pengembang **tidak bertanggung jawab** atas segala bentuk penyalahgunaan atau konsekuensi yang timbul dari penggunaan software ini. Seluruh risiko penggunaan berada pada pengguna masing-masing.
> 3. Seluruh merek dagang, nama sistem, materi silabus, dan data akademik adalah hak cipta dan hak milik sah dari **Universitas Bina Sarana Informatika** serta pemilik hak ciptanya masing-masing.
>
> **Permohonan Penghapusan / Pengarsipan (Takedown Notice)**:
> Jika pihak otoritas universitas atau pengelola sistem IT UBSI berkeberatan atas repositori ini, silakan hubungi pengelola langsung via GitHub ([@Curzyori](https://github.com/Curzyori)). Repositori ini akan dengan senang hati **diarsipkan atau dihapus permanen secara kooperatif**.

---

## <a id="why"></a>💡 Why UBSI API?

Layanan kampus UBSI tersebar di berbagai subdomain terpisah dengan antarmuka web konvensional (`studentv2`, `elearning`, `elibrary`, `repository`, `ejournal`, `news`). Mengambil jadwal kuliah atau mengecek tugas baru biasanya membutuhkan navigasi browser berulang-ulang.

UBSI API menyatukan seluruh sumber tersebut ke dalam satu backend JSON cepat di `127.0.0.1:8300` dengan proteksi keamanan tingkat tinggi:

| Fitur | Keterangan |
|---|---|
| ✅ **Dua Tingkat Cache (Redis DB 2)** | TTL berjenjang (Jadwal 2j, Nilai 30m, Tugas 10m) + Last-Known-Good fallback jika kampus offline |
| ✅ **Anti-Ban Protection** | Re-use session cookies in-memory, single-flight mutex per request, dan human jitter (0.8–1.5s) |
| ✅ **Browser TLS Impersonation** | Scrapling dengan `curl_cffi` desktop Chrome TLS signature; 100% identik dengan browser asli |
| ✅ **Normalized Clean JSON** | Sanitasi HTML otomatis; integer untuk SKS, float untuk nilai, dan ISO-8601 untuk tanggal |
| ✅ **Localhost Security Boundary** | Hanya mengikat ke `127.0.0.1:8300`; nol port ingress terbuka ke internet |
| ✅ **Native WordPress REST API** | Modul berita kampus mengambil langsung dari endpoint native JSON tanpa scraping HTML |

---

## <a id="key-features"></a>🎯 Key Features

| Modul | Status | Sumber | Kemampuan Utama |
|:---|:---:|:---|:---|
| **StudentV2** | ✅ | `students.bsi.ac.id` | Jadwal kuliah semester aktif, nilai murni, pengumuman PDF, arsip berita |
| **Elearning** | ✅ | `elearning.bsi.ac.id` (MyBest) | Kartu matkul, presensi perkuliahan, tugas & submission, materi ZIP, kuis |
| **Elibrary** | ✅ | `elibrary.bsi.ac.id` | OPAC search katalog, detail buku, stok fisik, 60s timeout & retry |
| **News Portal** | ✅ | `news.bsi.ac.id` | Berita kampus resmi via native WP REST API (`/wp-json/wp/v2/posts`) |
| **News Webhook** | ✅ | Internal Engine | Auto-dispatch webhook real-time setiap ada artikel baru via background worker |
| **Repository** | ✅ | `repository.bsi.ac.id` | Publikasi ilmiah terbaru & pencarian riset EPrints |
| **EJournal** | ✅ | `ejournal.bsi.ac.id` | Katalog 23 jurnal ilmiah resmi UBSI via jalur OAI bypass |
| **Rate Limiter** | ✅ | Internal Engine | Sliding-window limiter 60 request/menit via Redis |

---

## <a id="endpoints"></a>📡 Endpoints Reference (`/v1/`)

### Sistem
- `GET /health` — Status kesehatan aplikasi & koneksi Redis (`up`/`down`).
- `GET /metrics` — Metrik operasional scraper (jumlah sesi pool aktif & status Redis).

### StudentV2 (SIAKAD)
- `GET /v1/studentv2/dashboard` — Ambil jadwal, nilai, berita, dan pengumuman sekaligus secara paralel.
- `GET /v1/studentv2/schedule` — Jadwal kuliah semester aktif.
- `GET /v1/studentv2/grades` — Rekap nilai murni lengkap per mata kuliah.
- `GET /v1/studentv2/news` — Arsip pengumuman berita akademik.
- `GET /v1/studentv2/announcements` — Pengumuman edaran internal terbaru dari beranda.

### Elearning (MyBest LMS)
- `GET /v1/elearning/courses` — Daftar kartu mata kuliah aktif beserta token terenkripsi.
- `GET /v1/elearning/assignments` — Daftar tugas aktif & riwayat submission (nilai + komentar dosen).
- `GET /v1/elearning/presence` — Rekap status presensi perkuliahan per pertemuan.
- `GET /v1/elearning/materials` — Berkas silabus dan modul pembelajaran (ZIP/PDF).
- `GET /v1/elearning/quiz` — Jadwal kuis latihan dan ujian online aktif.

### Perpustakaan (Elibrary)
- `GET /v1/elibrary/search?q=&opsi=buku&page=1` — Pencarian katalog OPAC perpustakaan.
- `GET /v1/elibrary/book/{book_id}` — Detail metadata buku lengkap beserta stok fisik.

### Publikasi Ilmiah & Berita
- `GET /v1/news?search=&page=&per_page=` — Berita kampus resmi (dilengkapi author & featured image).
- `GET /v1/news/{post_id}` — Detail artikel berita lengkap.
- `POST /v1/news/webhook/test?target_url=` — Uji coba kirim payload event berita ke URL webhook target.
- `GET /v1/repository/recent` — Publikasi karya ilmiah dan tugas akhir terbaru di EPrints.
- `GET /v1/repository/search?q=` — Pencarian repositori karya ilmiah.
- `GET /v1/ejournal/journals` — Katalog lengkap 23 jurnal ilmiah resmi UBSI.

---

## <a id="tech-stack"></a>🛠️ Tech Stack

- **Backend API**: Python 3.12+, FastAPI, Uvicorn (uvloop).
- **Frontend Landing Page**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Anime.js (`animejs`).
- **Scraping & TLS**: Scrapling (FetcherSession), `curl_cffi` (Chrome impersonation), lxml.
- **Caching & Limiter**: Redis DB 2 (asyncio), Single-flight Mutex, Sliding Window Limiter.
- **Testing & Quality**: Pytest (78 passed), Pytest-Asyncio, HTTPX (ASGITransport).
- **Deployment & Hosting**: Vercel (`ubsi-api.muaraai.com`), Tencent Cloud VPS + PM2 + Caddy HTTPS.

---

## <a id="architecture"></a>🏗️ Architecture

```
UBSI-API/
├── app/                       # Backend FastAPI service (127.0.0.1:8300)
│   ├── modules/
│   │   ├── studentv2.py       # SIAKAD: Jadwal, Nilai, Berita, Pengumuman
│   │   ├── elearning.py       # MyBest: Captcha solver, Courses, Absensi, Tugas, Materi, Kuis
│   │   ├── elibrary.py        # Perpus: OPAC search, Book detail, 60s retry
│   │   ├── news.py            # Portal: Native WP REST API (/wp-json/wp/v2/posts)
│   │   ├── repository.py      # EPrints: Recent publications & search (/repo/{id}/)
│   │   └── ejournal.py        # OJS: 23 Active journals catalog with real titles
│   ├── cache.py               # Redis 2-tier cache (fresh + LGG) & single-flight mutex
│   ├── config.py              # Pydantic Settings & tiered TTLs
│   ├── deps.py                # Modular credential validation (Option B)
│   ├── envelope.py            # Clean Minimalist JSON envelope
│   ├── limiter.py             # Sliding window rate limiter (60 req/min)
│   ├── retry.py               # Exponential backoff retry with jitter
│   ├── router_helper.py       # Helper generik cache, lock, & SWR
│   ├── session_pool.py        # Pool sesi per-NIM dengan idle TTL (15m)
│   └── main.py                # Base FastAPI app & global middleware
├── web/                       # Frontend Landing Page (ubsi-api.muaraai.com)
│   ├── public/fonts/          # Self-hosted woff2 (Space Grotesk, Inter, JetBrains Mono)
│   ├── src/
│   │   ├── app/               # App Router, Layout, dynamic OG image, sitemap, robots
│   │   ├── components/        # Hero, CodeShowcase, ModulesGrid, Architecture, Quickstart
│   │   ├── data/              # Static datasets, code examples, roadmap
│   │   └── lib/               # Realtime GitHub stats & Health probe client
│   ├── tailwind.config.ts     # Deep Water design tokens (#0A1220, #2DD4BF)
│   └── package.json
├── tests/
│   ├── fixtures/              # Snapshot HTML offline
│   ├── conftest.py            # Fixture autouse & test auth client
│   └── test_*.py              # 71 Automated unit & integration tests
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
│   ├── api.md                 # 19 Endpoints dictionary & JSON payloads
│   ├── architecture.md        # Request lifecycle & cache flow
│   ├── anti-ban.md            # Account security & safety protocols
│   ├── deploy.md              # VPS PM2 production operations
│   └── remote-access.md       # Caddy, Nginx, & Cloudflare Tunnel guide
├── ecosystem.config.cjs       # PM2 production config untuk VPS
├── CONTRIBUTING.md            # Panduan kontribusi & layout tests
├── CODE_OF_CONDUCT.md         # Norma komunitas & etika rekayasa perangkat lunak
├── SECURITY.md                # Kebijakan etika & privasi akademik
├── DMCA.md                    # Kebijakan hak cipta & takedown notice
├── LICENSE                    # MIT License (c) 2026 Yuken Velino
└── requirements.txt           # Project dependencies
```

---

## <a id="quick-start"></a>🚀 Quick Start

### 1. Kloning & Persiapan
```bash
git clone https://github.com/MuaraAI/UBSI-API.git
cd UBSI-API

# Buat virtual environment & install dependensi
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Konfigurasi Environment
```bash
cp .env.example .env
# Edit .env:
# 1. API_KEY: Kunci rahasia untuk autentikasi endpoint terlindungi (X-API-Key).
#    Generate key: python3 -c "import secrets; print('ubsi_sec_' + secrets.token_hex(24))"
# 2. STUDENTV2_NIM & STUDENTV2_PASS: Akun mahasiswa untuk modul SIAKAD (students.bsi.ac.id).
# 3. ELEARNING_NIM & ELEARNING_PASS: Akun mahasiswa untuk modul MyBest LMS (elearning.bsi.ac.id).
# 4. Multi-Channel Webhook (Opsional):
#    - DISCORD_WEBHOOK_URL: Webhook URL channel Discord untuk Rich Embed berita kampus.
#    - TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID: Bot token & Chat ID untuk notifikasi berita via Telegram.
#    - NEWS_WEBHOOK_URL: Custom endpoint HTTP POST untuk bot WhatsApp Ciel / backend kustom.
```

### 3. Menjalankan Server & Contoh Request
```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8300 --reload
```

Dokumentasi interaktif OpenAPI/Swagger dapat diakses di:
👉 **`http://127.0.0.1:8300/docs`**

Contoh memanggil API dengan header autentikasi:
```bash
# Health check (tanpa auth)
curl -s http://127.0.0.1:8300/health

# Mengambil jadwal kuliah (wajib X-API-Key)
curl -s -H "X-API-Key: ubsi_s...xxx" http://127.0.0.1:8300/v1/studentv2/schedule

# Menguji broadcast berita ke Discord / Telegram / Custom webhook
curl -s -X POST -H "X-API-Key: ubsi_s...xxx" "http://127.0.0.1:8300/v1/news/webhook/test?channel=all"
```

---

## <a id="testing"></a>🧪 Testing

Semua parser diuji terhadap snapshot HTML offline tanpa melakukan request live ke kampus:

```bash
# Menjalankan seluruh test suite (78 tests)
.venv/bin/pytest -v

# Menjalankan live smoke test terhadap server lokal
.venv/bin/python scripts/smoke.py --base-url http://127.0.0.1:8300
```

---

## <a id="deployment"></a>🚀 Deployment ke VPS

Konfigurasi production menggunakan PM2 (`ecosystem.config.cjs`) di target folder `/home/ubuntu/ubsi-api`:

```bash
# Deploy otomatis 1-perintah via rsync & PM2 ke curzy-vps-tencent
./scripts/deploy.sh
```

---

## <a id="documentation"></a>📚 Documentation

- [API Reference](docs/api.md) — Kamus lengkap 19 endpoint beserta format request & response JSON.
- [System Architecture](docs/architecture.md) — Siklus request, two-tier cache, dan single-flight mutex.
- [Anti-Ban Protocol](docs/anti-ban.md) — Protokol proteksi akun kampus (cookie re-use, TLS impersonation, jitter).
- [Production Deployment](docs/deploy.md) — Panduan operasi dan pemeliharaan server VPS via PM2.
- [Remote Access & Domain](docs/remote-access.md) — Panduan setup Caddy, Nginx, Cloudflare Tunnel, dan otentikasi X-API-Key.
- [Agent Skill](skills/SKILL.md) — Panduan AI coding agent untuk konsumsi dan pengembangan otomatisasi UBSI API.

---

## <a id="contributors"></a>👥 Contributors

Proyek ini dibangun dan dikembangkan secara independen oleh mahasiswa aktif Universitas Bina Sarana Informatika (UBSI) Kampus Kota Pontianak:

| Foto | Kontributor | Identitas Mahasiswa | Peran | Commits |
|:---:|---|---|---|:---:|
| <img src="https://github.com/Curzyori.png" width="65" height="65" style="border-radius:50%;" alt="Yuken Velino" /> | **Yuken Velino**<br>[@Curzyori](https://github.com/Curzyori) | **NIM**: `15260767`<br>**Prodi**: Informatika (S1)<br>**Fakultas**: Teknik & Informatika<br>**Kelas**: `15.1C.30`<br>**Semester**: 1<br>**Kampus**: UBSI Kota Pontianak | **Lead Developer & Creator** | [![Commits](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FMuaraAI%2FUBSI-API%2Fcontributors&query=%24%5B0%5D.contributions&label=Commits&color=2DD4BF&logo=git)](https://github.com/MuaraAI/UBSI-API/commits?author=Curzyori) |
| <img src="https://github.com/MyKineID.png" width="65" height="65" style="border-radius:50%;" alt="Verzio" /> | **Verzio**<br>[@MyKineID](https://github.com/MyKineID) | **NIM**: `15260225`<br>**Prodi**: Informatika (S1)<br>**Fakultas**: Teknik & Informatika<br>**Kelas**: `15.1B.30`<br>**Semester**: 1<br>**Kampus**: UBSI Kota Pontianak | **Contributor** | [![Commits](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FMuaraAI%2FUBSI-API%2Fcontributors&query=%24%5B1%5D.contributions&label=Commits&color=2DD4BF&logo=git)](https://github.com/MuaraAI/UBSI-API/commits?author=MyKineID) |
| <img src="https://github.com/Seeyaa77.png" width="65" height="65" style="border-radius:50%;" alt="Muhammad Raffli Aldiansyah" /> | **Muhammad Raffli Aldiansyah**<br>[@Seeyaa77](https://github.com/Seeyaa77) | **NIM**: `15260161`<br>**Prodi**: Informatika (S1)<br>**Fakultas**: Teknik & Informatika<br>**Kelas**: `15.1A.30`<br>**Semester**: 1<br>**Kampus**: UBSI Kota Pontianak | **Contributor** | [![Commits](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FMuaraAI%2FUBSI-API%2Fcontributors&query=%24%5B2%5D.contributions&label=Commits&color=2DD4BF&logo=git)](https://github.com/MuaraAI/UBSI-API/commits?author=Seeyaa77) |

---

## <a id="roadmap"></a>🗺️ Roadmap

Rencana pengembangan dan milestones UBSI API:

### Version 1.0 (Current — Stable)
- [x] Read-Only aggregation untuk 6 modul resmi (`studentv2`, `elearning`, `elibrary`, `news`, `repository`, `ejournal`).
- [x] Caching dua tingkat (Redis DB 2) dengan fallback offline Last-Known-Good (`stale: true`).
- [x] Proteksi anti-ban (Chrome TLS signature, session cookie reuse, single-flight mutex).
- [x] Localhost security boundary (`127.0.0.1:8300`).
- [x] Session pool per-NIM dan parallel dashboard endpoint (`/v1/studentv2/dashboard`).
- [x] Metrik operasional scraper real-time (`/metrics`).
- [x] Helper generik `cached_endpoint` (PR #4) dan 58 pengujian otomatis lulus.

### Version 1.1 (Released — Security, Remote Ingress & Multi-Channel Webhooks)
- [x] **Mandatory API Key Authentication**:
  - Middleware `X-API-Key` dengan constant-time comparison (`secrets.compare_digest`).
  - Whitelist tunggal: `GET /health` untuk health probe monitoring.
  - Fail-Fast startup jika `API_KEY` kosong di `.env`.
- [x] **Dual-Path Remote Access**:
  - Dukungan Reverse Proxy (Caddy / Nginx) dengan HTTPS otomatis.
  - Dukungan Cloudflare Tunnel (`cloudflared`) untuk homelab / NAT tanpa IP publik.
- [x] **Real Client IP Rate Limiting**:
  - Ekstraksi IP asli via `CF-Connecting-IP` / `X-Forwarded-For` untuk mencegah tabrakan kuota di belakang proxy.
- [x] **CORS Support**:
  - `CORSMiddleware` terintegrasi untuk integrasi dashboard web frontend.
- [x] **Multi-Channel News Broadcaster (v1.1.5)**:
  - Auto-dispatch berita kampus baru secara paralel ke Discord (Rich Embed), Telegram (HTML photo message), dan Custom Webhook.
  - Migrasi domain upstream SIAKAD ke `students.bsi.ac.id`.

### Version 1.2.0 (In Progress — Feeds & Productivity)
- [ ] **Ekspor Kalender iCal (`.ics`)**:
  - Endpoint `GET /v1/studentv2/schedule.ics` untuk auto-sinkronisasi jadwal kuliah langsung ke Google Calendar (Android) dan Apple Calendar (iOS).
- [x] **Rekap Nilai Tugas & Kuis Elearning (Per Pertemuan)**:
  - Endpoint `GET /v1/elearning/grades` dan `GET /v1/elearning/courses/{id}/grades` untuk tracking status dan rekapitulasi nilai tugas, kuis, dan evaluasi 6 mata kuliah aktif per setiap pertemuan.
- [ ] **Bulk Downloader Modul & Silabus**:
  - Endpoint `GET /v1/elearning/materials/download-all` untuk mengunduh seluruh berkas materi perkuliahan 6 matkul sekaligus.
- [ ] **Kalkulator & Simulator IPK**:
  - Estimasi dan kalkulasi IPK/IPS real-time berdasarkan riwayat nilai murni.

### Version 2.0 (Planned — Full Interactive & Institutional)
- [ ] **Assignment Submission & Interactions**:
  - Pengunggahan & submit berkas tugas (`POST /v1/elearning/assignments/{id}/submit`).
  - Forum diskusi interaktif kelas.
- [ ] **Dosen & Staff Portal Mode (NIP Support)**:
  - Dukungan kredensial akun dosen/staf (`NIP_STUDENTV2` & `NIP_ELEARNING`).
  - Penarikan jadwal mengajar dosen & daftar peserta kelas per mata kuliah.
  - Rekap BAP (Berita Acara Perkuliahan).

---

## <a id="license"></a>⚖️ License & Legal

- **Lisensi**: MIT License — lihat berkas [LICENSE](LICENSE).
- **Kode Etik & Norma Komunitas**: Lihat berkas [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- **Kebijakan Keamanan**: Lihat berkas [SECURITY.md](SECURITY.md).
- **Pemberitahuan Hak Cipta & DMCA**: Lihat berkas [DMCA.md](DMCA.md).
- **Panduan Kontribusi**: Lihat berkas [CONTRIBUTING.md](CONTRIBUTING.md).

<p align="center">
  <sub>Developed by <b>Yuken Velino</b> (<a href="https://github.com/Curzyori">@Curzyori</a>) — NIM: 15260767 · Kelas: 15.1C.30 · Informatika · Fakultas Teknik & Informatika, UBSI Kampus Kota Pontianak</sub>
</p>
