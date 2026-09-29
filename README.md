<h1 align="center">UBSI API</h1>

<p align="center">
  <strong>REST API tidak resmi untuk enam layanan digital Universitas Bina Sarana Informatika</strong><br />
  StudentV2 (SIAKAD) · MyBest LMS · Elibrary · EJournal · Repository · News Portal — disatukan dalam satu antarmuka JSON.
</p>

<div align="center">

  <a href="https://ubsi-api.muaraai.com"><img src="https://img.shields.io/badge/website-ubsi--api.muaraai.com-2DD4BF?style=flat-square" alt="Website" /></a>
  <a href="https://github.com/MuaraAI/UBSI-API/blob/main/LICENSE"><img src="https://img.shields.io/github/license/MuaraAI/UBSI-API?style=flat-square&color=374151" alt="License" /></a>
  <img src="https://img.shields.io/badge/python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Redis-cache-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/tests-78%20lulus-2EA043?style=flat-square" alt="Tests" />

</div>

---

## Kontributor

Proyek ini dirintis, dibangun, dan dirawat secara independen oleh tiga mahasiswa Informatika UBSI Kampus Kota Pontianak. Seluruh dokumentasi di dalam repositori ini kami tulis dan perbarui sendiri secara manual — bukan hasil generator otomatis.

<table>
  <tr>
    <td align="center" width="33%">
      <a href="https://github.com/Curzyori">
        <img src="https://github.com/Curzyori.png" width="90" height="90" alt="Yuken Velino" style="border-radius:50%;" /><br />
        <b>Yuken Velino</b>
      </a>
      <br />
      <a href="https://github.com/Curzyori">@Curzyori</a>
      <br /><br />
      <a href="https://github.com/MuaraAI/UBSI-API/commits?author=Curzyori">
        <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FMuaraAI%2FUBSI-API%2Fcontributors&query=%24%5B0%5D.contributions&label=commits&color=2DD4BF&logo=git" alt="Commits" />
      </a>
      <br /><br />
      <sub><b>Lead Developer &amp; Creator</b><br />
      NIM 15260767 · Informatika (S1)<br />
      15.1C.30 · Semester 1<br />
      FTI · UBSI Kota Pontianak</sub>
    </td>
    <td align="center" width="33%">
      <a href="https://github.com/MyKineID">
        <img src="https://github.com/MyKineID.png" width="90" height="90" alt="Verzio Y." style="border-radius:50%;" /><br />
        <b>Verzio</b>
      </a>
      <br />
      <a href="https://github.com/MyKineID">@MyKineID</a>
      <br /><br />
      <a href="https://github.com/MuaraAI/UBSI-API/commits?author=MyKineID">
        <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FMuaraAI%2FUBSI-API%2Fcontributors&query=%24%5B1%5D.contributions&label=commits&color=2DD4BF&logo=git" alt="Commits" />
      </a>
      <br /><br />
      <sub><b>Core Contributor</b><br />
      NIM 15260225 · Informatika (S1)<br />
      15.1B.30 · Semester 1<br />
      FTI · UBSI Kota Pontianak</sub>
    </td>
    <td align="center" width="33%">
      <a href="https://github.com/Seeyaa77">
        <img src="https://github.com/Seeyaa77.png" width="90" height="90" alt="M Raffli Aldiansyah" style="border-radius:50%;" /><br />
        <b>M Raffli Aldiansyah</b>
      </a>
      <br />
      <a href="https://github.com/Seeyaa77">@Seeyaa77</a>
      <br /><br />
      <a href="https://github.com/MuaraAI/UBSI-API/commits?author=Seeyaa77">
        <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FMuaraAI%2FUBSI-API%2Fcontributors&query=%24%5B2%5D.contributions&label=commits&color=2DD4BF&logo=git" alt="Commits" />
      </a>
      <br /><br />
      <sub><b>Core Contributor</b><br />
      NIM 15260161 · Informatika (S1)<br />
      15.1A.30 · Semester 1<br />
      FTI · UBSI Kota Pontianak</sub>
    </td>
  </tr>
</table>

<p align="center">
  <a href="#disclaimer">Disclaimer</a> ·
  <a href="#latar-belakang">Latar Belakang</a> ·
  <a href="#fitur">Fitur</a> ·
  <a href="#endpoint">Endpoint</a> ·
  <a href="#teknologi">Teknologi</a> ·
  <a href="#struktur-proyek">Struktur</a> ·
  <a href="#memulai">Memulai</a> ·
  <a href="#dokumentasi">Dokumentasi</a> ·
  <a href="#roadmap">Roadmap</a> ·
  <a href="#lisensi">Lisensi</a>
</p>

---

## Disclaimer

> Proyek **UBSI API** adalah perangkat lunak tidak resmi (*unofficial*) yang dikembangkan secara independen oleh mahasiswa **Universitas Bina Sarana Informatika (UBSI)** untuk keperluan riset rekayasa perangkat lunak, otomatisasi personal, dan efisiensi waktu dalam mengakses jadwal, tugas, nilai, serta materi perkuliahan tanpa navigasi manual berulang.
>
> 1. Proyek ini **tidak berafiliasi resmi, tidak disponsori, dan tidak dikelola oleh pihak Universitas Bina Sarana Informatika (UBSI)**.
> 2. Pengembang **tidak bertanggung jawab** atas segala bentuk penyalahgunaan atau konsekuensi yang timbul dari penggunaan perangkat lunak ini. Seluruh risiko penggunaan berada pada pengguna masing-masing.
> 3. Seluruh merek dagang, nama sistem, materi silabus, dan data akademik adalah hak cipta dan hak milik sah dari **Universitas Bina Sarana Informatika** serta pemilik hak ciptanya masing-masing.
>
> **Permohonan Penghapusan / Pengarsipan (Takedown Notice)** — Jika pihak otoritas universitas atau pengelola sistem IT UBSI berkeberatan atas repositori ini, silakan hubungi pengelola langsung via GitHub ([@Curzyori](https://github.com/Curzyori)). Repositori ini akan dengan senang hati **diarsipkan atau dihapus permanen secara kooperatif**.

---

## Latar Belakang

Layanan akademik UBSI tersebar di enam subdomain terpisah — `studentv2`, `elearning`, `elibrary`, `ejournal`, `repository`, dan `news` — masing-masing dengan antarmuka web konvensional. Sekadar melihat jadwal kuliah atau memeriksa tugas baru berarti membuka browser, masuk log, lalu menelusuri halaman yang sama berulang kali.

UBSI API merapikan semuanya menjadi satu backend JSON yang cepat, berjalan lokal di `127.0.0.1:8300`, dan dilindungi lapisan-lapisan berikut:

| Lapisan | Penjelasan |
|---|---|
| **Cache dua tingkat (Redis DB 2)** | TTL berjenjang — jadwal 2 jam, nilai 30 menit, tugas 10 menit — plus fallback Last-Known-Good saat kampus offline |
| **Proteksi anti-ban** | Session cookie di-*reuse* in-memory, *single-flight mutex* per request, dan *human jitter* 0,8–1,5 detik |
| **TLS impersonation** | Scrapling dengan `curl_cffi` bersidik TLS desktop Chrome; pola trafik identik dengan browser asli |
| **JSON ternormalisasi** | Sanitasi HTML otomatis; SKS sebagai integer, nilai sebagai float, tanggal dalam format ISO-8601 |
| **Batas keamanan localhost** | Server hanya mengikat `127.0.0.1:8300`; nol port ingress terbuka ke internet |
| **WordPress REST API native** | Berita kampus diambil langsung dari endpoint JSON resmi, tanpa scraping HTML |

---

## Fitur

| Modul | Sumber | Kemampuan Utama |
|:---|:---|:---|
| **StudentV2** | `students.bsi.ac.id` | Jadwal kuliah semester aktif, nilai murni, pengumuman PDF, arsip berita |
| **Elearning** | `elearning.bsi.ac.id` (MyBest) | Kartu matkul, presensi perkuliahan, tugas & submission, materi ZIP, kuis |
| **Elibrary** | `elibrary.bsi.ac.id` | Pencarian katalog OPAC, detail buku, stok fisik, timeout 60 detik & retry |
| **News Portal** | `news.bsi.ac.id` | Berita kampus resmi via native WP REST API (`/wp-json/wp/v2/posts`) |
| **News Webhook** | Internal Engine | Auto-dispatch webhook real-time setiap ada artikel baru via background worker |
| **Repository** | `repository.bsi.ac.id` | Publikasi ilmiah terbaru & pencarian riset EPrints |
| **EJournal** | `ejournal.bsi.ac.id` | Katalog 23 jurnal ilmiah resmi UBSI via jalur OAI |
| **Rate Limiter** | Internal Engine | *Sliding-window* limiter 60 request/menit via Redis |

---

## Endpoint

### Sistem
- `GET /health` — Status kesehatan aplikasi dan koneksi Redis (`up`/`down`).
- `GET /metrics` — Metrik operasional scraper (jumlah sesi pool aktif dan status Redis).

### StudentV2 (SIAKAD)
- `GET /v1/studentv2/dashboard` — Jadwal, nilai, berita, dan pengumuman sekaligus secara paralel.
- `GET /v1/studentv2/schedule` — Jadwal kuliah semester aktif.
- `GET /v1/studentv2/grades` — Rekap nilai murni lengkap per mata kuliah.
- `GET /v1/studentv2/news` — Arsip pengumuman berita akademik.
- `GET /v1/studentv2/announcements` — Pengumuman edaran internal terbaru dari beranda.

### Elearning (MyBest LMS)
- `GET /v1/elearning/courses` — Daftar kartu mata kuliah aktif beserta token terenkripsi.
- `GET /v1/elearning/assignments` — Daftar tugas aktif dan riwayat submission (nilai + komentar dosen).
- `GET /v1/elearning/presence` — Rekap status presensi perkuliahan per pertemuan.
- `GET /v1/elearning/materials` — Berkas silabus dan modul pembelajaran (ZIP/PDF).
- `GET /v1/elearning/quiz` — Jadwal kuis latihan dan ujian online aktif.

### Perpustakaan (Elibrary)
- `GET /v1/elibrary/search?q=&opsi=buku&page=1` — Pencarian katalog OPAC perpustakaan.
- `GET /v1/elibrary/book/{book_id}` — Detail metadata buku lengkap beserta stok fisik.

### Publikasi Ilmiah & Berita
- `GET /v1/news?search=&page=&per_page=` — Berita kampus resmi (dengan author dan featured image).
- `GET /v1/news/{post_id}` — Detail artikel berita lengkap.
- `POST /v1/news/webhook/test?target_url=` — Uji kirim payload event berita ke URL webhook target.
- `GET /v1/repository/recent` — Publikasi karya ilmiah dan tugas akhir terbaru di EPrints.
- `GET /v1/repository/search?q=` — Pencarian repositori karya ilmiah.
- `GET /v1/ejournal/journals` — Katalog lengkap 23 jurnal ilmiah resmi UBSI.

---

## Teknologi

- **Backend API** — Python 3.12+, FastAPI, Uvicorn (uvloop).
- **Frontend Landing Page** — Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Anime.js.
- **Scraping & TLS** — Scrapling (FetcherSession), `curl_cffi` (Chrome impersonation), lxml.
- **Caching & Limiter** — Redis DB 2 (asyncio), single-flight mutex, sliding-window limiter.
- **Testing & Quality** — Pytest (78 lulus), Pytest-Asyncio, HTTPX (ASGITransport).
- **Deployment & Hosting** — Vercel (`ubsi-api.muaraai.com`), Tencent Cloud VPS + PM2 + Caddy HTTPS.

---

## Struktur Proyek

```
UBSI-API/
├── app/                       # Backend FastAPI service (127.0.0.1:8300)
│   ├── modules/
│   │   ├── studentv2.py       # SIAKAD: Jadwal, Nilai, Berita, Pengumuman
│   │   ├── elearning.py       # MyBest: Captcha solver, Courses, Absensi, Tugas, Materi, Kuis
│   │   ├── elibrary.py        # Perpus: OPAC search, Book detail, retry 60s
│   │   ├── news.py            # Portal: Native WP REST API (/wp-json/wp/v2/posts)
│   │   ├── repository.py      # EPrints: Recent publications & search (/repo/{id}/)
│   │   └── ejournal.py        # OJS: Katalog 23 jurnal aktif dengan judul asli
│   ├── cache.py               # Redis 2-tier cache (fresh + LGG) & single-flight mutex
│   ├── config.py              # Pydantic Settings & tiered TTLs
│   ├── deps.py                # Validasi kredensial modular (Option B)
│   ├── envelope.py            # Envelope JSON minimalis
│   ├── limiter.py             # Sliding-window rate limiter (60 req/menit)
│   ├── retry.py               # Exponential backoff retry dengan jitter
│   ├── router_helper.py       # Helper generik cache, lock, & SWR
│   ├── session_pool.py        # Pool sesi per-NIM dengan idle TTL (15 menit)
│   └── main.py                # Base FastAPI app & global middleware
├── web/                       # Frontend Landing Page (ubsi-api.muaraai.com)
│   ├── public/fonts/          # Self-hosted woff2 (Space Grotesk, Inter, JetBrains Mono)
│   ├── src/
│   │   ├── app/               # App Router, Layout, dynamic OG image, sitemap, robots
│   │   ├── components/        # Hero, CodeShowcase, ModulesGrid, Architecture, Quickstart
│   │   ├── data/              # Dataset statis, contoh kode, roadmap
│   │   └── lib/               # Realtime GitHub stats & Health probe client
│   ├── tailwind.config.ts     # Deep Water design tokens (#0A1220, #2DD4BF)
│   └── package.json
├── tests/
│   ├── fixtures/              # Snapshot HTML offline
│   ├── conftest.py            # Fixture autouse & test auth client
│   └── test_*.py              # 78 pengujian unit & integrasi otomatis
├── templates/
│   ├── Caddyfile.example      # Template reverse proxy Caddy (HTTPS otomatis)
│   ├── nginx.example.conf     # Template konfigurasi reverse proxy Nginx
│   └── cloudflared.example.yml# Template ingress Cloudflare Tunnel
├── scripts/
│   ├── deploy.sh              # Deploy satu perintah ke VPS Tencent via rsync & PM2
│   └── smoke.py               # CLI verifikasi live (8 pemeriksaan, auth-aware)
├── skills/
│   └── SKILL.md               # Definisi agent skill untuk asisten AI
├── docs/
│   ├── api.md                 # Kamus 19 endpoint & format payload JSON
│   ├── architecture.md        # Siklus request & alur cache
│   ├── anti-ban.md            # Protokol keamanan akun
│   ├── deploy.md              # Operasi produksi VPS via PM2
│   └── remote-access.md       # Panduan Caddy, Nginx, & Cloudflare Tunnel
├── ecosystem.config.cjs       # Konfigurasi produksi PM2 untuk VPS
├── CONTRIBUTING.md            # Panduan kontribusi & layout tests
├── CODE_OF_CONDUCT.md         # Norma komunitas & etika rekayasa perangkat lunak
├── SECURITY.md                # Kebijakan etika & privasi akademik
├── DMCA.md                    # Kebijakan hak cipta & takedown notice
├── LICENSE                    # MIT License (c) 2026 Yuken Velino
└── requirements.txt           # Dependensi proyek
```

---

## Memulai

### 1. Kloning dan Persiapan

```bash
git clone https://github.com/MuaraAI/UBSI-API.git
cd UBSI-API

# Buat virtual environment dan install dependensi
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Konfigurasi Environment

```bash
cp .env.example .env
```

Isi `.env` dengan:

1. **`API_KEY`** — Kunci rahasia untuk autentikasi endpoint terlindungi (header `X-API-Key`). Generate dengan:
   ```bash
   python3 -c "import secrets; print('ubsi_sec_' + secrets.token_hex(24))"
   ```
2. **`STUDENTV2_NIM` & `STUDENTV2_PASS`** — Akun mahasiswa untuk modul SIAKAD (`students.bsi.ac.id`).
3. **`ELEARNING_NIM` & `ELEARNING_PASS`** — Akun mahasiswa untuk modul MyBest LMS (`elearning.bsi.ac.id`).
4. **Multi-channel webhook (opsional)**:
   - `DISCORD_WEBHOOK_URL` — Webhook channel Discord untuk Rich Embed berita kampus.
   - `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` — Notifikasi berita via Telegram.
   - `NEWS_WEBHOOK_URL` — Endpoint HTTP POST kustom untuk bot WhatsApp Ciel / backend lain.

### 3. Menjalankan Server

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8300 --reload
```

Dokumentasi interaktif OpenAPI/Swagger tersedia di `http://127.0.0.1:8300/docs`.

Contoh pemanggilan API dengan header autentikasi:

```bash
# Health check (tanpa auth)
curl -s http://127.0.0.1:8300/health

# Mengambil jadwal kuliah (wajib X-API-Key)
curl -s -H "X-API-Key: ubsi_s...xxx" http://127.0.0.1:8300/v1/studentv2/schedule

# Menguji broadcast berita ke Discord / Telegram / webhook kustom
curl -s -X POST -H "X-API-Key: ubsi_s...xxx" "http://127.0.0.1:8300/v1/news/webhook/test?channel=all"
```

---

## Pengujian

Semua parser diuji terhadap snapshot HTML offline, tanpa request live ke server kampus:

```bash
# Menjalankan seluruh test suite (78 tests)
.venv/bin/pytest -v

# Live smoke test terhadap server lokal
.venv/bin/python scripts/smoke.py --base-url http://127.0.0.1:8300
```

---

## Deployment

Konfigurasi produksi menggunakan PM2 (`ecosystem.config.cjs`) di target folder `/home/ubuntu/ubsi-api`:

```bash
# Deploy otomatis satu perintah via rsync & PM2 ke curzy-vps-tencent
./scripts/deploy.sh
```

---

## Dokumentasi

- [API Reference](docs/api.md) — Kamus lengkap 19 endpoint beserta format request dan response JSON.
- [System Architecture](docs/architecture.md) — Siklus request, two-tier cache, dan single-flight mutex.
- [Anti-Ban Protocol](docs/anti-ban.md) — Protokol proteksi akun kampus (cookie re-use, TLS impersonation, jitter).
- [Production Deployment](docs/deploy.md) — Panduan operasi dan pemeliharaan server VPS via PM2.
- [Remote Access & Domain](docs/remote-access.md) — Setup Caddy, Nginx, Cloudflare Tunnel, dan otentikasi `X-API-Key`.
- [Agent Skill](skills/SKILL.md) — Panduan AI coding agent untuk konsumsi dan pengembangan otomatisasi UBSI API.

Panduan kontribusi tersedia di [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Roadmap

### v1.0 — Stabil (Rilis)
- [x] Agregasi read-only untuk 6 modul (`studentv2`, `elearning`, `elibrary`, `news`, `repository`, `ejournal`).
- [x] Cache dua tingkat (Redis DB 2) dengan fallback offline Last-Known-Good (`stale: true`).
- [x] Proteksi anti-ban (Chrome TLS signature, session cookie reuse, single-flight mutex).
- [x] Batas keamanan localhost (`127.0.0.1:8300`).
- [x] Session pool per-NIM dan endpoint dashboard paralel (`/v1/studentv2/dashboard`).
- [x] Metrik operasional scraper real-time (`/metrics`).
- [x] Helper generik `cached_endpoint` (PR #4) dan 58 pengujian otomatis lulus.

### v1.1 — Keamanan, Remote Ingress & Multi-Channel Webhook (Rilis)
- [x] **Autentikasi API key wajib** — middleware `X-API-Key` dengan constant-time comparison (`secrets.compare_digest`), whitelist `GET /health` untuk health probe, dan fail-fast startup jika `API_KEY` kosong.
- [x] **Dual-path remote access** — reverse proxy (Caddy/Nginx) dengan HTTPS otomatis, atau Cloudflare Tunnel (`cloudflared`) untuk homelab tanpa IP publik.
- [x] **Rate limiting real client IP** — ekstraksi IP asli via `CF-Connecting-IP` / `X-Forwarded-For` agar kuota tidak bertabrakan di belakang proxy.
- [x] **Dukungan CORS** — `CORSMiddleware` terintegrasi untuk integrasi dashboard web frontend.
- [x] **Multi-channel news broadcaster (v1.1.5)** — auto-dispatch berita baru paralel ke Discord (Rich Embed), Telegram (HTML photo message), dan custom webhook; migrasi upstream SIAKAD ke `students.bsi.ac.id`.

### v1.2 — Feeds & Produktivitas (Dikerjakan)
- [ ] **Ekspor kalender iCal (`.ics`)** — endpoint `GET /v1/studentv2/schedule.ics` untuk sinkronisasi jadwal kuliah ke Google Calendar (Android) dan Apple Calendar (iOS).
- [x] **Rekap nilai tugas & kuis elearning per pertemuan** — endpoint `GET /v1/elearning/grades` dan `GET /v1/elearning/courses/{id}/grades` untuk melacak status dan rekapitulasi nilai tugas, kuis, dan evaluasi 6 mata kuliah aktif.
- [ ] **Bulk downloader modul & silabus** — endpoint `GET /v1/elearning/materials/download-all` untuk mengunduh seluruh materi 6 matkul sekaligus.
- [ ] **Kalkulator & simulator IPK** — estimasi IPK/IPS real-time berdasarkan riwayat nilai murni.

### v2.0 — Interaktif Penuh & Institusional (Direncanakan)
- [ ] **Assignment submission & interaksi** — pengunggahan berkas tugas (`POST /v1/elearning/assignments/{id}/submit`) dan forum diskusi kelas.
- [ ] **Dosen & staff portal mode (NIP)** — dukungan kredensial dosen/staf (`NIP_STUDENTV2` & `NIP_ELEARNING`), jadwal mengajar, daftar peserta kelas, dan rekap BAP (Berita Acara Perkuliahan).

---

## Lisensi

- **Lisensi** — MIT License, lihat [LICENSE](LICENSE).
- **Kode etik & norma komunitas** — [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- **Kebijakan keamanan** — [SECURITY.md](SECURITY.md).
- **Hak cipta & DMCA** — [DMCA.md](DMCA.md).
- **Panduan kontribusi** — [CONTRIBUTING.md](CONTRIBUTING.md).

<p align="center">
  <sub>Dikembangkan oleh <b>Yuken Velino</b> (<a href="https://github.com/Curzyori">@Curzyori</a>) — NIM 15260767 · Kelas 15.1C.30 · Informatika · Fakultas Teknik &amp; Informatika, UBSI Kampus Kota Pontianak</sub>
</p>
