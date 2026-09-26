# UBSI API

Private, unofficial REST API yang mengagregasi layanan web kampus Universitas Bina Sarana Informatika (UBSI) ke dalam satu endpoint JSON terpadu dengan perlindungan anti-ban dan caching dua tingkat.

---

## Layanan & Cakupan Data

| Modul | Sumber | Status Akses | Data yang Disediakan |
|---|---|---|---|
| `studentv2` | `studentv2.bsi.ac.id` | Autentikasi (NIM/Password) | Jadwal kuliah, nilai murni, pengumuman internal PDF, arsip berita |
| `elearning` | `elearning.bsi.ac.id` (MyBest) | Autentikasi (NIM/Password + Math Captcha) | Kartu matkul, presensi perkuliahan, tugas & submission, materi zip, kuis online |
| `elibrary` | `elibrary.bsi.ac.id` | Publik | OPAC search katalog, detail buku, eksemplar & stok |
| `news` | `news.bsi.ac.id` | Publik (Native WP REST API) | Berita kampus resmi (judul, penulis, media gambar, konten lengkap) |
| `repository` | `repository.bsi.ac.id` | Publik (EPrints) | Publikasi ilmiah terbaru & pencarian riset |
| `ejournal` | `ejournal.bsi.ac.id` | Publik (OAI Bypass) | Katalog 16 jurnal ilmiah resmi UBSI |

---

## Daftar Endpoint (Prefix `/v1/`)

### 1. Sistem & Pemantauan
- `GET /health` — Status server dan konektivitas Redis (`up`/`down`).

### 2. StudentV2 (SIAKAD)
- `GET /v1/studentv2/schedule` — Jadwal kuliah semester aktif.
- `GET /v1/studentv2/grades` — Rekap nilai murni per mata kuliah (UTS, UAS, Tugas, Absen, Total, Grade).
- `GET /v1/studentv2/news` — Arsip berita pengumuman mahasiswa.
- `GET /v1/studentv2/announcements` — Pengumuman edaran internal terbaru dari beranda.

### 3. Elearning (MyBest LMS)
- `GET /v1/elearning/courses` — Daftar kartu mata kuliah aktif & token terenkripsi.
- `GET /v1/elearning/assignments` — Daftar tugas aktif dan riwayat submission (nilai & komentar dosen).
- `GET /v1/elearning/presence` — Rekap status presensi perkuliahan per pertemuan.
- `GET /v1/elearning/materials` — Berkas silabus dan modul pembelajaran (ZIP/PDF).
- `GET /v1/elearning/quiz` — Jadwal kuis latihan dan ujian online aktif.

### 4. Perpustakaan (Elibrary)
- `GET /v1/elibrary/search?q=&opsi=buku&page=1` — Pencarian katalog OPAC perpustakaan.
- `GET /v1/elibrary/book/{book_id}` — Detail metadata buku lengkap beserta ketersediaan stok fisik.

### 5. Publikasi Ilmiah & Berita
- `GET /v1/news?search=&page=&per_page=` — Daftar berita resmi dari WordPress REST API BSI.
- `GET /v1/news/{post_id}` — Detail artikel berita lengkap.
- `GET /v1/repository/recent` — Publikasi karya ilmiah dan skripsi terbaru di EPrints repository.
- `GET /v1/repository/search?q=` — Pencarian repositori karya ilmiah.
- `GET /v1/ejournal/journals` — Katalog 16 jurnal ilmiah resmi UBSI.

---

## Format Respons

Semua respons menggunakan format Clean Minimalist JSON:

```json
{
  "success": true,
  "data": [ ... ],
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

## Menjalankan Server

```bash
# Salin konfigurasi environment
cp .env.example .env
# Isi kredensial NIM/Password di .env

# Jalankan server
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8300
```

Dokumentasi interaktif OpenAPI/Swagger dapat diakses di `http://127.0.0.1:8300/docs`.

---

## Tautan Dokumen

- **Panduan Kontribusi**: Lihat [`CONTRIBUTING.md`](CONTRIBUTING.md) untuk setup development, panduan pengujian TDD, dan struktur folder `tests/`.
- **Kebijakan Keamanan & Etika**: Lihat [`SECURITY.md`](SECURITY.md) untuk batasan penggunaan pribadi dan proteksi anti-ban.
- **Lisensi**: MIT License — lihat [`LICENSE`](LICENSE).
