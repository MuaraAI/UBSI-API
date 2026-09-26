# UBSI API

Private, unofficial REST API yang mengagregasi layanan web kampus Universitas Bina Sarana Informatika (UBSI) ke dalam satu endpoint JSON terpadu dengan perlindungan anti-ban dan caching dua tingkat.

---

## 1. Sumber Layanan

| Modul | Sumber | Status Akses | Scope Data |
|---|---|---|---|
| `studentv2` | `studentv2.bsi.ac.id` | Autentikasi (NIM/Password) | Jadwal kuliah, nilai murni, pengumuman internal PDF, arsip berita |
| `elearning` | `elearning.bsi.ac.id` (MyBest) | Autentikasi (NIM/Password + Math Captcha) | Kartu matkul, presensi per pertemuan, tugas & submission, materi zip, kuis |
| `elibrary` | `elibrary.bsi.ac.id` | Publik | OPAC search katalog, detail buku, eksemplar & stok |
| `news` | `news.bsi.ac.id` | Publik (Native WP REST API) | Berita kampus resmi (judul, penulis, media gambar, konten lengkap) |
| `repository` | `repository.bsi.ac.id` | Publik (EPrints) | Publikasi ilmiah terbaru & pencarian riset |
| `ejournal` | `ejournal.bsi.ac.id` | Publik (OAI Bypass) | Katalog 16 jurnal ilmiah resmi UBSI |

---

## 2. Arsitektur & Keamanan

- **Localhost Boundary**: Aplikasi hanya mengikat ke `127.0.0.1:8300` (tidak pernah diekspos ke publik di v1).
- **Anti-Ban Protections**:
  - Re-use cookie sesi in-memory (tidak mengirim request login berulang).
  - Single-Flight Mutex: Request konkuren untuk endpoint yang sama tidak akan menembak server kampus secara paralel.
  - Browser Fingerprint: Scrapling dengan `curl_cffi` Chrome TLS impersonation (identik 100% dengan Google Chrome di desktop).
- **Caching Dua Tingkat (Redis DB 2)**:
  - *Cache Segar* dengan TTL berjenjang (Jadwal: 2 jam, Nilai: 30 menit, Tugas: 10 menit, Berita: 15 menit, Perpus: 1 jam).
  - *Last-Known-Good (LGG)* tanpa batas waktu: Jika server kampus down, API tetap menyajikan data terakhir yang sukses dengan penanda `"stale": true`.
- **Response Format**: Clean Minimalist JSON:
  ```json
  {
    "success": true,
    "data": [...],
    "cached": false
  }
  ```

---

## 3. Instalasi & Menjalankan Lokal

### Prasyarat
- Python 3.12+
- `uv` (Fast Python package manager)
- Redis Server aktif lokal atau remote (`redis://127.0.0.1:6379/2`)

### Langkah Menjalankan
```bash
# 1. Clone repository
git clone https://github.com/Curzyori/UBSI-API.git
cd UBSI-API

# 2. Buat virtual environment & install dependensi
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# 3. Konfigurasi environment
cp .env.example .env
# Edit .env dengan kredensial NIM/Password kampus Anda

# 4. Jalankan server
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8300 --reload
```

---

## 4. Pengujian (Testing)

Semua parser HTML diuji terhadap snapshot fixture offline di `tests/fixtures/` tanpa melakukan request live ke server kampus saat pengujian otomatis.

```bash
# Menjalankan seluruh test suite
.venv/bin/pytest -v

# Menjalankan live smoke test terhadap server lokal
.venv/bin/python scripts/smoke.py --base-url http://127.0.0.1:8300
```

---

## 5. Deployment ke VPS (PM2)

Konfigurasi production menggunakan PM2 (`ecosystem.config.cjs`) di target folder `/home/ubuntu/ubsi-api`:

```bash
# Deploy otomatis 1-perintah via rsync & PM2
./scripts/deploy.sh
```

---

## 6. Lisensi & Etika

- **Lisensi**: MIT License (lihat berkas `LICENSE`).
- **Kebijakan Keamanan**: Lihat berkas `SECURITY.md`.
- **Panduan Kontribusi**: Lihat berkas `CONTRIBUTING.md`.
