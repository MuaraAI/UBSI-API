<h1 align="center">UBSI API</h1>
<p align="center">
  <strong>Private Unofficial REST API Aggregator for UBSI Services</strong>
</p>

<p align="center">
  Unified JSON interface for StudentV2 (SIAKAD), MyBest LMS, Elibrary, EJournal, Repository, and News Portal.
</p>

<div align="center">

  <a href="https://github.com/Curzyori/UBSI-API"><img src="https://img.shields.io/badge/status-active-success?style=for-the-badge&color=374151" alt="Status" /></a>
  <a href="https://github.com/Curzyori/UBSI-API/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Curzyori/UBSI-API?style=for-the-badge&color=374151" alt="License" /></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&color=374151" alt="Python Version" />
  <img src="https://img.shields.io/badge/framework-FastAPI-teal?style=for-the-badge&color=374151" alt="FastAPI" />
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
  <a href="#license">License</a>
</p>

---

## <a id="disclaimer"></a>⚠️ PENTING / DISCLAIMER RESMI

> **Pernyataan Penafian (Disclaimer)**:
> 
> Proyek **UBSI API** ini adalah software *unofficial* (tidak resmi) yang dikembangkan secara independen oleh **Yuken Velino** (NIM: **15260767**, Kelas: **15.1C.30**), mahasiswa **Program Studi Informatika, Fakultas Teknik & Informatika, Universitas Bina Sarana Informatika (UBSI) Kampus Kota Pontianak** semata-mata untuk **keperluan riset edukasi rekayasa perangkat lunak, otomatisasi personal, dan efisiensi waktu**. Proyek ini dibuat agar mahasiswa dan developer kampus dapat mengakses informasi jadwal, nilai, tugas, dan materi kuliah mereka sendiri secara terstruktur tanpa perlu melakukan navigasi manual yang memakan waktu setiap hari.
>
> 1. Proyek ini **sama sekali tidak berafiliasi resmi, tidak disponsori, dan tidak dikelola oleh Universitas Bina Sarana Informatika (UBSI)**.
> 2. Pengembang/maintainer **tidak bertanggung jawab** atas segala bentuk penyalahgunaan, kerugian, atau pelanggaran ketentuan yang timbul akibat penggunaan software ini. Seluruh penggunaan menjadi tanggung jawab pribadi masing-masing pengguna.
> 3. Seluruh nama, logo, merek dagang, materi perkuliahan, dan data akademik adalah hak cipta dan hak milik sah dari **Universitas Bina Sarana Informatika** serta pemilik hak ciptanya masing-masing.
>
> **Permohonan Penghapusan / Pengarsipan (Takedown Notice)**:
> Jika pihak rektorat, dekanat, dosen, atau pengelola sistem IT UBSI yang berwenang merasa keberatan atas keberadaan repositori atau endpoint ini, silakan hubungi pengelola langsung via GitHub ([@Curzyori](https://github.com/Curzyori)). Repositori ini akan dengan senang hati **diarsipkan, diubah, atau dihapus secara kooperatif**.

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
| **StudentV2** | ✅ | `studentv2.bsi.ac.id` | Jadwal kuliah semester aktif, nilai murni, pengumuman PDF, arsip berita |
| **Elearning** | ✅ | `elearning.bsi.ac.id` (MyBest) | Kartu matkul, presensi perkuliahan, tugas & submission, materi ZIP, kuis |
| **Elibrary** | ✅ | `elibrary.bsi.ac.id` | OPAC search katalog, detail buku, stok fisik, 60s timeout & retry |
| **News Portal** | ✅ | `news.bsi.ac.id` | Berita kampus resmi via native WP REST API (`/wp-json/wp/v2/posts`) |
| **Repository** | ✅ | `repository.bsi.ac.id` | Publikasi ilmiah terbaru & pencarian riset EPrints |
| **EJournal** | ✅ | `ejournal.bsi.ac.id` | Katalog 16 jurnal ilmiah resmi UBSI via jalur OAI bypass |
| **Rate Limiter** | ✅ | Internal Engine | Sliding-window limiter 60 request/menit via Redis |

---

## <a id="endpoints"></a>📡 Endpoints Reference (`/v1/`)

### Sistem
- `GET /health` — Status kesehatan aplikasi & koneksi Redis (`up`/`down`).

### StudentV2 (SIAKAD)
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
- `GET /v1/repository/recent` — Publikasi karya ilmiah dan tugas akhir terbaru di EPrints.
- `GET /v1/repository/search?q=` — Pencarian repositori karya ilmiah.
- `GET /v1/ejournal/journals` — Katalog 16 jurnal ilmiah resmi UBSI.

---

## <a id="tech-stack"></a>🛠️ Tech Stack

- **Runtime & Web**: Python 3.12+, FastAPI, Uvicorn (uvloop).
- **Scraping & TLS**: Scrapling (FetcherSession), `curl_cffi` (Chrome impersonation), lxml.
- **Caching & Limiter**: Redis DB 2 (asyncio), Single-flight Mutex, Sliding Window Limiter.
- **Testing & Quality**: Pytest, Pytest-Asyncio, HTTPX (ASGITransport).
- **Process Manager**: PM2 (`ecosystem.config.cjs`).

---

## <a id="architecture"></a>🏗️ Architecture

```
UBSI-API/
├── app/
│   ├── modules/
│   │   ├── studentv2.py       # SIAKAD: Jadwal, Nilai, Berita, Pengumuman
│   │   ├── elearning.py       # MyBest: Captcha solver, Courses, Absensi, Tugas, Materi, Kuis
│   │   ├── elibrary.py        # Perpus: OPAC search, Book detail, 60s retry
│   │   ├── news.py            # Portal: Native WP REST API (/wp-json/wp/v2/posts)
│   │   ├── repository.py      # EPrints: Recent publications & search
│   │   └── ejournal.py        # OJS: 16 Journal catalog via OAI bypass
│   ├── cache.py               # Redis 2-tier cache (fresh + LGG) & single-flight mutex
│   ├── config.py              # Pydantic Settings & tiered TTLs
│   ├── deps.py                # Modular credential validation (Option B)
│   ├── envelope.py            # Clean Minimalist JSON envelope
│   ├── limiter.py             # Sliding window rate limiter (60 req/min)
│   └── main.py                # Base FastAPI app & global middleware
├── tests/
│   ├── fixtures/              # Snapshot HTML offline
│   └── test_*.py              # 46 Automated unit & integration tests
├── scripts/
│   ├── deploy.sh              # 1-klik deploy ke VPS Tencent via rsync & PM2
│   └── smoke.py               # Live verification CLI tool
├── ecosystem.config.cjs       # PM2 production config untuk VPS
├── CONTRIBUTING.md            # Panduan kontribusi & layout tests
├── SECURITY.md                # Kebijakan etika & privasi akademik
├── DMCA.md                    # Kebijakan hak cipta & takedown notice
├── LICENSE                    # MIT License (c) 2026 Yuken Velino
└── requirements.txt           # Project dependencies
```

---

## <a id="quick-start"></a>🚀 Quick Start

### 1. Kloning & Persiapan
```bash
git clone https://github.com/Curzyori/UBSI-API.git
cd UBSI-API

# Buat virtual environment & install dependensi
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Konfigurasi Environment
```bash
cp .env.example .env
# Edit .env dan masukkan NIM serta Password UBSI Anda
```

### 3. Menjalankan Server
```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8300 --reload
```

Dokumentasi interaktif OpenAPI/Swagger dapat diakses di:
👉 **`http://127.0.0.1:8300/docs`**

---

## <a id="testing"></a>🧪 Testing

Semua parser diuji terhadap snapshot HTML offline tanpa melakukan request live ke kampus:

```bash
# Menjalankan seluruh test suite (46 tests)
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

- [API Reference](docs/api.md) — Kamus lengkap 17 endpoint beserta format request & response JSON.
- [System Architecture](docs/architecture.md) — Siklus request, two-tier cache, dan single-flight mutex.
- [Anti-Ban Protocol](docs/anti-ban.md) — Protokol proteksi akun kampus (cookie re-use, TLS impersonation, jitter).
- [Production Deployment](docs/deploy.md) — Panduan operasi dan pemeliharaan server VPS via PM2.
- [Agent Skill](skills/SKILL.md) — Panduan AI coding agent untuk konsumsi dan pengembangan otomatisasi UBSI API.

---

## <a id="license"></a>⚖️ License & Legal

- **Lisensi**: MIT License — lihat berkas [LICENSE](LICENSE).
- **Kebijakan Keamanan**: Lihat berkas [SECURITY.md](SECURITY.md).
- **Pemberitahuan Hak Cipta & DMCA**: Lihat berkas [DMCA.md](DMCA.md).
- **Panduan Kontribusi**: Lihat berkas [CONTRIBUTING.md](CONTRIBUTING.md).

<p align="center">
  <sub>Developed by <b>Yuken Velino</b> (<a href="https://github.com/Curzyori">@Curzyori</a>) — NIM: 15260767 · Kelas: 15.1C.30 · Informatika · Fakultas Teknik & Informatika, UBSI Kampus Kota Pontianak</sub>
</p>
