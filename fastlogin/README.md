# FastLogin MyBest — Masuk Cepat Hanya dengan NIM

Folder khusus untuk login cepat ke `elearning.bsi.ac.id` (MyBest) tanpa mengetik
password/captcha setiap kali, plus alat pengindeks NIM.

## Kenapa "hanya NIM" itu bisa?

| Lapisan keamanan | Cara fastlogin menanganinya |
|---|---|
| Captcha (Kode Keamanan) | **Dibypass otomatis** — kode dirender sebagai teks SVG di HTML sehingga terbaca langsung (strategi 1). Ada juga strategi pola matematika & atribut. |
| Password | **Diingat terenkripsi** — ditanya sekali saat pertama (`Fernet`, kunci mesin di `store/machine.key`), login berikutnya cukup NIM. |
| Sesi | **Cookie sesi disimpan** per NIM — masuk instan selama sesi hidup. |
| Sistem keamanan berubah | **Fallback berlapis** — bila captcha berubah jadi gambar/teknik lain, tool otomatis mundur ke mode manual (buka `store/captcha_terbaru.*`, ketik kodenya), lalu strategi baru bisa ditambahkan di `solve_captcha_auto`. |

> Catatan jujur: password **tidak bisa di-bypass sungguhan** — server tetap
> memverifikasinya. Yang dilakukan tool ini adalah menyimpannya terenkripsi di
> komputermu agar tidak perlu mengetiknya lagi. Tidak ada akses ke akun orang
> lain tanpa password mereka.

## Pemakaian

Jalankan dari root repo dengan virtual environment yang sudah ada:

```bash
# Sekali saja: pasang dependensi enkripsi
.venv/Scripts/python -m pip install cryptography

# Login — password ditanya sekali, selanjutnya cukup NIM
.venv/Scripts/python fastlogin/main.py login 15260767

# Indeks seluruh NIM yang terlihat oleh akun tersebut
.venv/Scripts/python fastlogin/main.py index 15260767

# Lihat hasil indeks
.venv/Scripts/python fastlogin/main.py show

# Lupa password tersimpan / keluar
.venv/Scripts/python fastlogin/main.py forget 15260767
```

Opsi penting:

- `--base-url <URL>` — target lain (mis. mock server untuk pengujian).
- `--manual-captcha` — paksa mode manual bila sistem keamanan berubah dan
  strategi otomatis gagal.
- `--pages N` — batas halaman yang diramban saat `index`.

## Struktur

```
fastlogin/
├── main.py          # CLI utama (login / index / show / forget)
├── devmock.py       # Mock server MyBest untuk uji offline (tidak menyentuh kampus)
└── store/           # GITIGNORE — jangan di-commit!
    ├── machine.key          # Kunci Fernet untuk enkripsi password
    ├── credentials.enc      # Password per NIM (terenkripsi)
    ├── sessions/<NIM>.json  # Cookie sesi per NIM
    └── nim_index.json       # Hasil pengindeksan NIM
```

## Cara kerja `index`

Masuk dengan sesi tersimpan, lalu meramban (BFS, maks `--pages` halaman)
seluruh tautan same-origin yang bisa dijangkau akun, dan mengambil setiap
teks berpola NIM (`15\d{6}` — pola angkatan Informatika; bisa diganti via
`NIM_PATTERN` di `main.py`). Hasilnya terkumpul di `store/nim_index.json`
lengkap dengan waktu terakhir terlihat.

## Uji cepat tanpa menyentuh kampus

```bash
# Terminal 1 — mock MyBest lokal (login dengan password "mockpass")
.venv/Scripts/python fastlogin/devmock.py

# Terminal 2 — pakai tool melawan mock
.venv/Scripts/python fastlogin/main.py login 15260767 --password mockpass --base-url http://127.0.0.1:8765
.venv/Scripts/python fastlogin/main.py index 15260767 --base-url http://127.0.0.1:8765
.venv/Scripts/python fastlogin/main.py show
```

## Etika & batasan

Tool ini untuk akunmu sendiri. Mengindeks NIM hanya menampilkan data yang
terlihat oleh akun yang dipakai masuk. Tetap patuhi `SECURITY.md` dan
`anti-ban.md` di root repo — jangan spam request ke server kampus.
