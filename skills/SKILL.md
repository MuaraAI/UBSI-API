---
name: ubsi-api
version: 1.0.0
description: Agent skill for consuming, extending, and operating the UBSI API (Unofficial BSI Campus Aggregator).
metadata:
  repository: https://github.com/Curzyori/UBSI-API
  author: Yuken Velino (@Curzyori)
  nim: "15260767"
  class: 15.1C.30
  program: Informatika
  faculty: Teknik & Informatika
  institution: Universitas Bina Sarana Informatika (UBSI) Kampus Kota Pontianak
  license: MIT
  tags: [ubsi, api, studentv2, mybest, scraping, redis, fastapi]
---

# UBSI API Agent Skill

Panduan operasional dan referensi teknis bagi AI Coding Agent dan pengembang yang berinteraksi dengan, mengembangkan, atau mengonsumsi layanan **UBSI API** (`127.0.0.1:8300`).

---

## 1. Project & Author Overview

- **Repository**: [https://github.com/Curzyori/UBSI-API](https://github.com/Curzyori/UBSI-API) (Private)
- **Author**: **Yuken Velino** ([@Curzyori](https://github.com/Curzyori)) — NIM: `15260767` · Kelas: `15.1C.30` · Informatika · FTI UBSI Pontianak.
- **Contributor**: **Verzio** ([@MyKineID](https://github.com/MyKineID)) — NIM: `15260225` · Kelas: `15.1B.30` · Informatika · FTI UBSI Pontianak (PR #2).
- **Tujuan**: Otomatisasi personal dan jembatan data terstruktur JSON (jadwal, nilai, tugas, materi) untuk bot asisten mahasiswa dan developer tanpa navigasi manual.
- **Dokumentasi Lengkap**:
  - [`README.md`](../README.md) — Gambaran umum produk, ringkasan endpoint, dan quick start.
  - [`CONTRIBUTING.md`](../CONTRIBUTING.md) — Tata cara kontribusi, alur PR, dan struktur pengujian `tests/`.
  - [`SECURITY.md`](../SECURITY.md) — Kebijakan privasi, kredensial lokal, dan etika keamanan.
  - [`DMCA.md`](../DMCA.md) — Hak cipta kampus, landasan *Fair Use*, dan permohonan takedown resmi.
  - [`docs/api.md`](../docs/api.md) — Kamus detail 18 endpoint beserta contoh payload JSON.
  - [`docs/architecture.md`](../docs/architecture.md) — Diagram siklus request, two-tier cache, dan mutex.
  - [`docs/anti-ban.md`](../docs/anti-ban.md) — Protokol proteksi akun kampus (TLS impersonation, session reuse, jitter).
  - [`docs/deploy.md`](../docs/deploy.md) — Panduan operasi dan pemeliharaan server production via PM2.

---

## 2. Kemampuan & Endpoint Utama (`/v1/`)

| Domain | Key Endpoints | Deskripsi & Scope |
|---|---|---|
| **Sistem** | `GET /health` | Status server dan konektivitas Redis (`status: "ok"`) |
| **SIAKAD** | `GET /v1/studentv2/dashboard`<br>`GET /v1/studentv2/schedule`<br>`GET /v1/studentv2/grades`<br>`GET /v1/studentv2/announcements`<br>`GET /v1/studentv2/news` | Dashboard paralel (4 seksi sekaligus), jadwal kuliah aktif, nilai murni lengkap (UTS/UAS/Tugas/Grade), edaran PDF, dan arsip berita |
| **MyBest LMS** | `GET /v1/elearning/courses`<br>`GET /v1/elearning/assignments`<br>`GET /v1/elearning/presence`<br>`GET /v1/elearning/materials`<br>`GET /v1/elearning/quiz` | Kartu matkul & token terenkripsi, deadline tugas & nilai dosen, rekap presensi hadir, tautan ZIP silabus/modul, kuis online |
| **Perpustakaan** | `GET /v1/elibrary/search?q={query}&opsi={buku}`<br>`GET /v1/elibrary/book/{book_id}` | Pencarian OPAC katalog, metadata buku, klasifikasi, dan stok fisik di rak |
| **Berita Resmi** | `GET /v1/news?page={1}&per_page={10}&search={query}`<br>`GET /v1/news/{id}` | Berita kampus resmi langsung via native WordPress REST API (`news.bsi.ac.id`) |
| **Publikasi** | `GET /v1/repository/recent`<br>`GET /v1/repository/search?q={query}`<br>`GET /v1/ejournal/journals` | EPrints skripsi/penelitian terbaru dan katalog 16 jurnal ilmiah resmi UBSI via OAI bypass |

---

## 3. Standar Format Respons (Clean Minimalist JSON)

Setiap endpoint mengembalikan format envelope standar:

```json
{
  "success": true,
  "data": [...],
  "cached": false
}
```

Format respons kesalahan:
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

## 4. Aturan Penting & Skenario "Jika Ini, Maka Itu" (Rules & Scenarios)

### Skenario 1: Kredensial Kosong di `.env`
- **Aturan**: Modul publik (`/health`, `/v1/news`, `/v1/elibrary`, `/v1/repository`, `/v1/ejournal`) harus tetap berjalan normal 100%.
- **Jika** endpoint privat (`/v1/studentv2/*` atau `/v1/elearning/*`) dipanggil saat kredensial kosong:
  - Kembalikan HTTP 400 dengan error code `CONFIG_MISSING` (jangan sampai server crash atau melempar 500).

### Skenario 2: Server Kampus Sedang Down / Maintenance
- **Aturan**: Jangan biarkan bot atau script consumer mengalami blank/crash.
- **Jika** upstream kampus timeout atau gagal dihubungi:
  - Cek cache **Last-Known-Good (LGG)** di Redis.
  - Jika ada data tersimpan, sajikan data tersebut dengan penanda `"stale": true` dan `"cached": true`.
  - Hanya lemparkan HTTP 502 `UPSTREAM_ERROR` jika data LGG sama sekali belum pernah tersimpan.

### Skenario 3: Sesi Cookie Kampus Kedaluwarsa
- **Aturan**: Jangan mengirim request login berulang kali jika sesi masih valid.
- **Jika** response dari kampus mengarah kembali ke URL `/login`:
  - Lakukan re-login otomatis sebanyak 1 kali di latar belakang.
  - Ulangi request ke URL tujuan secara transparan bagi consumer.

### Skenario 4: Menambah atau Mengubah Scraper/Parser
- **Aturan**: Pengujian wajib menerapkan TDD dan berjalan 100% offline.
- **Jika** membuat parser baru atau memperbarui parser yang rusak:
  - Simpan snapshot HTML ke dalam folder `tests/fixtures/`.
  - Unit test pytest (`.venv/bin/pytest -v`) harus membaca dari fixture tersebut tanpa melakukan live hit ke server kampus.

### Skenario 5: Permohonan Takedown Otoritas Kampus
- **Aturan**: Mengedepankan itikad baik (*good faith*) dan kepatuhan akademik.
- **Jika** pihak berwenang kampus mengajukan keberatan:
  - Ikuti prosedur di [`DMCA.md`](../DMCA.md) untuk menonaktifkan endpoint atau mengarsipkan repositori secara kooperatif.

---

## 5. Deployment & Operasional Lingkungan (VPS / Server)

Setiap pengguna atau server memiliki konfigurasi path, user, dan port yang berbeda-beda. **Jangan berasumsi menggunakan path hardcoded.**

- Untuk setup dan konfigurasi production, rujuk selalu ke:
  - [`docs/deploy.md`](../docs/deploy.md) — Panduan konfigurasi PM2, environment variables, dan pemeliharaan server.
  - [`ecosystem.config.cjs`](../ecosystem.config.cjs) — Contoh konfigurasi PM2.
  - [`scripts/deploy.sh`](../scripts/deploy.sh) — Script deployment otomatis yang dapat disesuaikan per variabel `VPS_HOST`, `REMOTE_DIR`, dan `REMOTE_VENV`.
- Untuk pengujian kesehatan live setelah deploy:
  ```bash
  .venv/bin/python scripts/smoke.py --base-url http://127.0.0.1:8300
  ```
