# UBSI API — Design Spec

Date: 2026-09-25
Status: Approved in chat, pending user spec review
Owner: Yuken Velino

## 1. Apa ini

Private, unofficial REST API yang menyatukan layanan web Universitas Bina Sarana Informatika ke dalam satu endpoint JSON. Consumer: tooling pribadi user (curzy-student, Ciel bot, skrip) yang jalan di VPS yang sama.

Sources:
- studentv2.bsi.ac.id (SIAKAD — login)
- elearning.bsi.ac.id (MyBest LMS — login)
- elibrary.bsi.ac.id (katalog perpus — publik)
- ejournal.bsi.ac.id (jurnal — Cloudflare-protected)
- repository.bsi.ac.id (EPrints — publik)
- bsi.ac.id (portal berita/pengumuman — publik)

## 2. Non-goals

- Bukan API publik. Tidak ada manajemen user, tidak ada rate limit per-client, tidak ada domain/TLS.
- Tidak menyimpan state akademik. Status "sudah dibaca / baru" ditentukan consumer via Supabase-nya masing-masing; API hanya menyajikan data + `id` stabil per item.
- Tidak ada UI.

## 3. Keputusan (disetujui user)

| Aspek | Keputusan |
|---|---|
| Scope Operasi | Read-Only di v1 (Write operations seperti auto-absen/submit tugas ditunda ke v2) |
| Audiens | Pribadi, 1 user |
| Modul | 6 (studentv2, elearning, elibrary, ejournal, repository, news) |
| Stack | Python 3.12+, FastAPI, Scrapling (Fetcher / FetcherSession with curl_cffi Chrome impersonation) |
| Dev | Laptop; deploy ke VPS Tencent via script |
| Binding | 127.0.0.1:8300 (VPS dan lokal) — tidak pernah 0.0.0.0 |
| Route Prefix | `/v1/` (contoh: `/v1/studentv2/schedule`, `/v1/elearning/courses`) |
| Domain / HTTPS | Skip di v1 (YAGNI) — evaluasi di v2 jika ada kebutuhan akses publik |
| Auth API | Tanpa API key di v1 (localhost boundary murni) |
| Rate Limit | 60 req/menit via Redis sliding window counter |
| Response Format | Clean Minimalist JSON: `{"success": true, "data": ..., "cached": false}` |
| Cache | Redis lokal: fresh TTL ~60s + last-known-good tanpa TTL |
| Persistensi | Redis saja; tanpa SQLite, tanpa ORM |

## 4. Arsitektur

Satu app FastAPI, satu file per modul, tanpa database:

```
request → Rate Limiter (Redis 60 req/min)
            └─ if exceeded → 429 Too Many Requests
            └─ if allowed  → Route Handler → Cache Manager
                                ├─ Cache Hit (fresh, TTL 60s) → return {"success": true, "data": ..., "cached": true}
                                └─ Cache Miss → Fetcher Module
                                      ├─ Fetch live (Scrapling session)
                                      ├─ if redirect to /login → Auto re-login 1x & retry
                                      ├─ Parse & Sanitize (clean types: int, float, null, stripped str)
                                      ├─ Save to Redis: fresh (EX 60s) AND lgg (no TTL)
                                      └─ Return {"success": true, "data": ..., "cached": false}
                                
        Scrape / Upstream Gagal:
            ├─ Cek LGG (Last-Known-Good) di Redis
            ├─ Ada LGG → return {"success": true, "data": lgg, "cached": true, "stale": true}
            └─ Tidak ada LGG → return 502 {"success": false, "error": {"code": "UPSTREAM_DOWN", ...}}
```

### Aturan Logika & Percabangan (Control Flow Rules)

1. **Cache Fallback Logic (LGG)**:
   - Cache Segar (TTL 60s): Menahan spamming request ke server kampus.
   - Last-Known-Good (Tanpa TTL): Jika kampus timeout/down/maintenance, balikan data terakhir yang pernah sukses dengan status `"stale": true` agar consumer (Ciel / bot) tidak pernah crash atau blank.

2. **Auto Re-Login Logic**:
   - Jika response URL mengarah kembali ke `*/login`, session mendeteksi cookie kedaluwarsa.
   - Lakukan `session.login()` ulang otomatis sebanyak 1 kali.
   - Jika login ulang sukses, ulangi request ke URL target.
   - Jika login ulang gagal, baru lemparkan error `AUTH_FAILED`.

3. **Empty Data vs Layout Changed**:
   - Jika tabel/data bernilai kosong (`len(rows) == 0`):
     - Jika penanda halaman resmi ada (misal judul "Jadwal Kuliah"): dianggap sah memang sedang tidak ada jadwal/tugas → return `{"success": true, "data": []}`.
     - Jika penanda halaman resmi hilang: struktur HTML kampus diasumsikan berubah → lemparkan `HTML_STRUCTURE_CHANGED`.

4. **Data Sanitization Rules**:
   - String: selalu pangkas whitespace ganda (`" ".join(val.split()).strip()`).
   - Angka/SKS: parse ke `int`, jika bernilai `"-"` atau kosong → default `0`.
   - Nilai/Grade: parse ke `float`, jika bernilai `"-"` atau belum dinilai → `null`.
   - Waktu/Tanggal: format standar ISO-8601 string.

5. **Handling Kredensial Kosong (Modular Check — Opsi B)**:
   - Server tidak mati total jika kredensial `.env` belum diisi.
   - Endpoint publik (`/v1/news`, `/v1/elibrary`, `/v1/repository`, `/health`) tetap beroperasi 100% tanpa butuh login.
   - Jika endpoint privat (`/v1/studentv2/*` atau `/v1/elearning/*`) diakses saat env terkait kosong:
     - Kembalikan HTTP 400 dengan JSON bersih:
       ```json
       {
         "success": false,
         "error": {
           "code": "CONFIG_MISSING",
           "message": "STUDENTV2_NIM dan STUDENTV2_PASS belum diatur di .env",
           "module": "studentv2"
         }
       }
       ```

Komponen:

- `app/cache.py` — wrapper redis.asyncio: `get_fresh`, `set_fresh`, `get_lgg`, `set_lgg`. Key = `sha256(modul + path + params)`. Dua key per entry: `ubsi:fresh:{h}` (EX 60), `ubsi:lgg:{h}` (no TTL).
- `app/envelope.py` — satu bentuk respons bersih (Clean Minimalist JSON):
  ```json
  {
    "success": true,
    "data": ...,
    "cached": false
  }
  ```
  Error:
  ```json
  {
    "success": false,
    "error": {
      "code": "UPSTREAM_TIMEOUT",
      "message": "Deskripsi error jelas",
      "module": "studentv2"
    }
  }
  ```
  dengan HTTP status 502 (upstream error) / 429 (rate limit exceeded) / 500 (internal bug).
- `app/limiter.py` — Redis sliding window rate limiter: max 60 req/menit per client IP/ID.
- `app/session.py` — Scrapling FetcherSession per modul login-an (cookie jar persisten in-memory), helper re-login sekali saat redirect ke halaman login terdeteksi. Sleep acak kecil (0.5–1.5s) antar request ber-paginasi ke kampus.
- `app/<modul>.py` — masing-masing: fungsi fetch + parser murni (parse(html) → dict) yang bisa dites tanpa jaringan.

## 5. Endpoint (v1) — dikunci dari hasil audit live 25 Sep 2026

Hasil audit: presensi ternyata ada di MyBest (bukan studentv2); tagihan TIDAK
ada di kedua portal (sistem pembayaran terpisah) — di-drop dari scope.
Semua URL `/absen-mhs/{enc}`, `/assignment/{enc}`, `/learning/{enc}` pakai
token Laravel terenkripsi — diperlakukan opaque, selalu diambil dari `/sch`.

```
GET /health                        → { status, redis: up/down }

# studentv2 (login CSRF _token; terbukti di ubsi_sync.py)
GET /v1/studentv2/announcements    → beranda: pengumuman internal (PDF) + menu berita
GET /v1/studentv2/news             → /mahasiswa/berita (608 baris; pagination/cap)
GET /v1/studentv2/schedule         → /mahasiswa/jadwal-kuliah
                                     [No,Hari,Jam,Kode Dosen,Kode,MK,SKS,Kel.Pratek,Ruang,Bahan Ajar]
GET /v1/studentv2/grades           → /mahasiswa/nilai-murni
                                     [No,Kode,MK,SKS,UTS,UAS,Tugas,Absen,Total,Grade]
GET /v1/studentv2/khs              → /mahasiswa/khs [No,Kode,MK,SKS,Nilai,Mutu,Ket]
GET /v1/studentv2/krs              → /mahasiswa/krs [No,Kode,MK,SKS,Paraf]

# elearning MyBest (login CSRF + captcha matematika; terbukti di ubsi_sync.py)
GET /v1/elearning/courses          → /sch: kartu matkul (nama,kode dosen,kode mtk,
                                     sks,ruang,kel praktek,kode gabung,hari,jam) + token
GET /v1/elearning/presence         → /absen-mhs/{enc}
                                     [#,Status Absen,Tanggal,MK,Pertemuan,Rangkuman,Berita Acara]
GET /v1/elearning/assignments      → /assignment/{enc} (2 tabel):
                                     tugas [No,Kode Mtk,Kelas,Judul,Des,Pertemuan,Mulai,Selesai,Aksi]
                                     submission [Judul,Link Tugas,Komentar Dosen,Nilai]
GET /v1/elearning/materials        → /learning/{enc} [No,Kode Mtk,Kelas,Judul,Deskripsi,File]
                                     file host: students.bsi.ac.id (silabus/modul zip)
GET /v1/elearning/quiz             → /exercise [No,Kode Mtk,Paket,Dosen,Waktu,Mulai,Selesai,Aksi]

# elibrary (publik, custom PHP, server LAMBAT — timeout 60s + retry wajib)
GET /v1/elibrary/search?q=&opsi=buku|semua|ta|skripsi|jurnal|prosiding|ebook&page
    → GET /opac/pingresult?q={q}&opsi={opsi}; "Ditemukan N hasil";
      paginasi /opac/result/?q=&o={opsi}&pg={offset}
GET /v1/elibrary/categories        → /opac/buku|ebook|jurnal|prosiding|referensi|skripsi|tugasakhir
GET /v1/elibrary/book/{id}         → /readbook/{id}/{slug}.html
                                     KV: kode, klasifikasi, judul, edisi, penulis,
                                     penerbit, bahasa, tahun, ISBN, tajuk subjek,
                                     deskripsi/sinopsis, eksemplar, stok
GET /v1/elibrary/news              → /news (+ /readnews/{y}/{m}/{id}/slug)

# publik (audit menyusul saat modulnya dibangun)
GET /v1/ejournal/search?q=&page=   GET /v1/ejournal/article/{id}
GET /v1/repository/search?q=&page= GET /v1/repository/item/{id}
# news portal (news.bsi.ac.id — terbukti punya WordPress REST API aktif)
GET /v1/news?page=1&per_page=10&search=   → proxy/transform ke https://news.bsi.ac.id/wp-json/wp/v2/posts?_embed=1
                                          (Native JSON, full content, author, featured image, no HTML scraping)
GET /v1/news/feed                         → https://news.bsi.ac.id/feed/ (RSS XML/JSON)
GET /v1/news/{id}                         → https://news.bsi.ac.id/wp-json/wp/v2/posts/{id}?_embed=1
```

`id` item = hash stabil dari URL/judul sumber (dipakai consumer untuk deteksi item baru).

### Catatan audit (25 Sep 2026)

- Login kedua situs SUKSES via fungsi `ubsi_sync.py` (Study-Curzy) — logika dipakai ulang.
- `/mahasiswa/khs-semester`, `/mahasiswa/nilai-uts`, `/mahasiswa/uts`, `/mahasiswa/kalender`
  kosong/seasonal — endpoint khusus hanya kalau nanti dibutuhkan.
- `/halaman-ujian` (MyBest) redirect loop saat tidak ada ujian aktif — tidak dijadikan endpoint.
- studentv2 beranda juga mengekspos PDF pengumuman internal per-fakultas (sumber announcements).

### Catatan audit elibrary (25 Sep 2026)

- Bukan SLiMS/Koha — custom PHP CodeIgniter-ish. robots.txt hanya blokir `/cgi-bin/`.
- Search: `/opac/pingresult?q=...&opsi=...` (GET, butuh `opsi`; tanpa itu respons kosong).
  Verified live: `q=metode&opsi=buku` → "Ditemukan 967 hasil", 20 item/halaman.
- Paginasi: `/opac/result/?q=...&o=buku&pg=N` (pg=10 = hal. 2; pola offset — konfirmasi ulang saat build).
- Detail `/readbook/{id}/{slug}.html` = tabel KV lengkap + sinopsis + stok.
  Tombol "Download" + pembaca PDF (pdf.js) ada tapi butuh login member (loginmember) —
  v1 sajikan metadata + stok saja, baca/download buku bukan scope.
- Bonus koleksi: tugas akhir `/tugasakhir/{nim}/{slug}` + berita perpustakaan.
- Server sering timeout 30s+ — client wajib timeout 60s + retry 3x exponential.

### Catatan audit ejournal (25 Sep 2026)

- Cloudflare challenge menutup `/ejurnal/` root dan `/ejurnal/index.php/*` (semua jurnal OJS,
  16 judul terpetakan dari fallback). Plain httpx 403; Obscura stealth pun belum lolos.
- CELAH: `/ejurnal/oai?verb=Identify` dilayani TANPA challenge (fallback ke homepage) —
  katalog jurnal tetap bisa diambil.
- Keputusan final di M6, urutan: (1) curl_cffi impersonate Chrome → (2) flaresolverr
  (butuh docker di VPS) → (3) fallback: modul ejournal mode katalog-only via celah oai.

## 6. Cloudflare (ejournal)

Plan A: httpx polos dengan header browser wajar. Plan B (hanya jika terblokir): modul ejournal fetch via Obscura stealth (`obscura fetch --dump html`), sisanya tetap httpx. Keputusan diambil saat membangun modul ejournal, bukan sekarang.

## 7. Struktur repo

```
UBSI-API/
  app/ main.py cache.py envelope.py session.py
       studentv2.py elearning.py elibrary.py ejournal.py repository.py news.py
  tests/            # parser tests vs fixture HTML tersimpan di tests/fixtures/
  fixtures/         # snapshot HTML halaman kampus (tanpa data sensitif)
  scripts/deploy.sh # rsync ke VPS + restart systemd
  scripts/smoke.py  # live check sekali jalan: login + 1 endpoint per modul
  .env.example      # STUDENTV2_USER, STUDENTV2_PASS, ELEARNING_USER,
                    # ELEARNING_PASS, REDIS_URL, PORT
  requirements.txt  # fastapi, uvicorn, httpx, selectolax, redis
```

`.env` di-gitignore; modular check saat request (endpoint publik tetap jalan jika kredensial privat belum diisi).

## 8. Testing

- Parser murni = fungsi `parse(html)`, dites lawan fixture HTML hasil snapshot manual (dibersihkan dari data pribadi). Situs berubah layout → test merah sebelum produksi kena.
- Envelope + cache: unit test kecil (fakeredis atau redis lokal).
- `scripts/smoke.py`: verifikasi live end-to-end sekali jalan sebelum tiap deploy.
- Tidak ada test framework berat: pytest saja.

## 9. Deploy

- `scripts/deploy.sh`: rsync `app/` + `requirements.txt` → `pip install -r` di venv VPS → `systemctl restart ubsi-api`.
- systemd unit: `ExecStart=uvicorn app.main:app --host 127.0.0.1 --port 8300`, `Restart=always`, user non-root.
- RAM: ~60–80MB, aman di sisa ~900MB VPS.

## 10. Security & etika

- Kredensial kampus hanya di `.env` VPS/laptop; tidak pernah masuk git, log, atau respons API.
- Bind 127.0.0.1 — satu-satunya boundary akses. Tidak dibuka ke publik; kebutuhan akses jarak jauh lewat SSH tunnel.
- Polling manusiawi: cache 60s menahan beban ke kampus; sleep antar halaman paginasi.
- Bersifat akses data pribadi sendiri (nilai/tagihan/tugas akun sendiri) + halaman publik.

## 11. Milestone

1. M1 — Skeleton: FastAPI + envelope + cache redis + /health
2. M2 — studentv2 (login, announcements, schedule, grades, bills, presence)
3. M3 — elearning (courses, materials, assignments)
4. M4 — repository + elibrary (publik, cepat)
5. M5 — news
6. M6 — ejournal (dengan keputusan Cloudflare A/B)
7. M7 — deploy.sh + systemd + smoke di VPS

## 12. Terbuka

- Bentuk persis endpoint & parsing tiap modul dikunci saat modul dibangun (discovery terhadap situs asli).
- Username/password elearning vs studentv2 diduga sama (SSO) — dikonfirmasi di M2.
