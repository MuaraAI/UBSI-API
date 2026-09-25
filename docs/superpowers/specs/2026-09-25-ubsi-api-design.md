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
| Audiens | Pribadi, 1 user |
| Modul | 6 (semua sumber di atas) |
| Stack | Python 3.12+, FastAPI, httpx (AsyncClient), selectolax |
| Dev | Laptop; deploy ke VPS Tencent via script |
| Binding | 127.0.0.1:8300 (VPS dan lokal) — tidak pernah 0.0.0.0 |
| Auth API | Tidak ada (localhost-only adalah boundary-nya) |
| Cache | Redis lokal (sudah ada di VPS): fresh TTL ~60s + last-known-good tanpa TTL |
| Persistensi | Redis saja; tanpa SQLite, tanpa ORM |

## 4. Arsitektur

Satu app FastAPI, satu file per modul, tanpa database:

```
request → FastAPI route → cache get (redis)
                            ├─ hit fresh → return
                            └─ miss → modul: login (jika perlu, cookie jar
                                      AutoLogin: re-login diam-diam saat
                                      cookie mati) → fetch httpx → parse
                                      selectolax → SET fresh (EX 60)
                                      + SET lgg (no TTL) → return
        scrape/parse gagal → baca lgg → return data + stale_since
        lgg juga kosong   → 502 envelope
```

Komponen:

- `app/cache.py` — wrapper redis.asyncio: `get_fresh`, `set_fresh`, `get_lgg`, `set_lgg`. Key = `sha256(modul + path + params)`. Dua key per entry: `ubsi:fresh:{h}` (EX 60), `ubsi:lgg:{h}` (no TTL).
- `app/envelope.py` — satu bentuk respons:
  ```json
  { "ok": true, "data": ..., "source": "<url sumber>", "fetched_at": "<iso8601>", "stale_since": null }
  ```
  Error: `{ "ok": false, "error": { "module": "studentv2", "kind": "login_failed|upstream_error|parse_error", "detail": "..." } }` dengan status 502 (upstream) / 500 (bug kita).
- `app/session.py` — AsyncClient per modul login-an (cookie jar persisten in-memory), helper re-login sekali saat redirect ke halaman login terdeteksi. Sleep acak kecil (0.5–1.5s) antar request ber-paginasi ke kampus.
- `app/<modul>.py` — masing-masing: fungsi fetch + parser murni (parse(html) → dict) yang bisa dites tanpa jaringan.

## 5. Endpoint (v1) — dikunci dari hasil audit live 25 Sep 2026

Hasil audit: presensi ternyata ada di MyBest (bukan studentv2); tagihan TIDAK
ada di kedua portal (sistem pembayaran terpisah) — di-drop dari scope.
Semua URL `/absen-mhs/{enc}`, `/assignment/{enc}`, `/learning/{enc}` pakai
token Laravel terenkripsi — diperlakukan opaque, selalu diambil dari `/sch`.

```
GET /health                        → { status, redis: up/down }

# studentv2 (login CSRF _token; terbukti di ubsi_sync.py)
GET /studentv2/announcements       → beranda: pengumuman internal (PDF) + menu berita
GET /studentv2/news                → /mahasiswa/berita (608 baris; pagination/cap)
GET /studentv2/schedule            → /mahasiswa/jadwal-kuliah
                                     [No,Hari,Jam,Kode Dosen,Kode,MK,SKS,Kel.Pratek,Ruang,Bahan Ajar]
GET /studentv2/grades              → /mahasiswa/nilai-murni
                                     [No,Kode,MK,SKS,UTS,UAS,Tugas,Absen,Total,Grade]
GET /studentv2/khs                 → /mahasiswa/khs [No,Kode,MK,SKS,Nilai,Mutu,Ket]
GET /studentv2/krs                 → /mahasiswa/krs [No,Kode,MK,SKS,Paraf]

# elearning MyBest (login CSRF + captcha matematika; terbukti di ubsi_sync.py)
GET /elearning/courses             → /sch: kartu matkul (nama,kode dosen,kode mtk,
                                     sks,ruang,kel praktek,kode gabung,hari,jam) + token
GET /elearning/presence            → /absen-mhs/{enc}
                                     [#,Status Absen,Tanggal,MK,Pertemuan,Rangkuman,Berita Acara]
GET /elearning/assignments         → /assignment/{enc} (2 tabel):
                                     tugas [No,Kode Mtk,Kelas,Judul,Des,Pertemuan,Mulai,Selesai,Aksi]
                                     submission [Judul,Link Tugas,Komentar Dosen,Nilai]
GET /elearning/materials           → /learning/{enc} [No,Kode Mtk,Kelas,Judul,Deskripsi,File]
                                     file host: students.bsi.ac.id (silabus/modul zip)
GET /elearning/quiz                → /exercise [No,Kode Mtk,Paket,Dosen,Waktu,Mulai,Selesai,Aksi]

# elibrary (publik, custom PHP, server LAMBAT — timeout 60s + retry wajib)
GET /elibrary/search?q=&opsi=buku|semua|ta|skripsi|jurnal|prosiding|ebook&page
    → GET /opac/pingresult?q={q}&opsi={opsi}; "Ditemukan N hasil";
      paginasi /opac/result/?q=&o={opsi}&pg={offset}
GET /elibrary/categories           → /opac/buku|ebook|jurnal|prosiding|referensi|skripsi|tugasakhir
GET /elibrary/book/{id}            → /readbook/{id}/{slug}.html
                                     KV: kode, klasifikasi, judul, edisi, penulis,
                                     penerbit, bahasa, tahun, ISBN, tajuk subjek,
                                     deskripsi/sinopsis, eksemplar, stok
GET /elibrary/news                 → /news (+ /readnews/{y}/{m}/{id}/slug)

# publik (audit menyusul saat modulnya dibangun)
GET /ejournal/search?q=&page=      GET /ejournal/article/{id}
GET /repository/search?q=&page=    GET /repository/item/{id}
GET /news                          → portal berita (news.bsi.ac.id/feed/ sudah ada di curzy_digest)
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

`.env` di-gitignore, fail-fast saat startup kalau var login tidak ada (modul publik tidak butuh kredensial).

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
