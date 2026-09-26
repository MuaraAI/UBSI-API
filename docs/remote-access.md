# Panduan Remote Access & Deployment Domain (UBSI API v1.1)

UBSI API dirancang dengan prinsip **Localhost-Only Security Boundary**: aplikasi berjalan murni di `127.0.0.1:8300` dan tidak pernah mengekspos port aplikasi secara langsung ke `0.0.0.0` publik.

Untuk mengakses API dari luar (aplikasi mobile, dashboard web, atau bot eksternal), tersedia dua jalur yang didukung secara resmi:
1. **Jalur A: Reverse Proxy (Caddy / Nginx)** — Direkomendasikan untuk VPS ber-IP publik.
2. **Jalur B: Cloudflare Tunnel (`cloudflared`)** — Direkomendasikan untuk laptop / homelab / VPS tanpa port publik (di balik CGNAT).

Semua akses remote diwajibkan menyertakan header keamanan **`X-API-Key`**.

---

## 1. Persiapan Konfigurasi Lingkungan (`.env`)

Sebelum membuka akses remote, pastikan 3 variabel keamanan di berkas `.env` server sudah terpasang:

```bash
# Generate kunci rahasia 48 karakter acak:
python3 -c "import secrets; print('ubsi_sec_' + secrets.token_hex(24))"
```

Tempelkan ke berkas `.env`:
```bash
# 1. Kunci akses utama (Wajib diisi di produksi)
API_KEY=ubsi_sec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 2. Kebijakan Browser / CORS (Default: * — semua origin diizinkan)
ALLOWED_ORIGINS=*

# 3. IP Proxy Terpercaya untuk Real Client IP (Default: 127.0.0.1)
TRUSTED_PROXIES=127.0.0.1
```

### Rincian Fungsi Variabel:

1. **`API_KEY` (Mandatory Authentication)**:
   - Kunci gerbang utama. Semua endpoint non-health (`/v1/*`, `/metrics`, dll.) wajib menyertakan header `X-API-Key`.
   - UBSI API menerapkan *fail-fast startup*: jika `API_KEY` belum disetel di `.env`, aplikasi menolak berjalan demi mencegah kebocoran data pribadi ke publik.

2. **`ALLOWED_ORIGINS` (Izin Browser / CORS Policy)**:
   - Mengatur website atau dashboard frontend mana saja yang diizinkan memanggil API ini lewat JavaScript di browser.
   - Nilai `*` (*wildcard*, default): Memungkinkan frontend web dari domain apa pun memanggil API. Tetap aman karena setiap request tetap harus menyertakan `X-API-Key` yang valid.
   - Nilai spesifik: Jika ingin mengunci hanya untuk website dashboard tertentu, masukkan URL asal dipisahkan koma, contoh:
     ```bash
     ALLOWED_ORIGINS=https://dashboard.example.com,http://localhost:3000
     ```

3. **`TRUSTED_PROXIES` (Pencegahan Spoofing Real Client IP)**:
   - Mengatur alamat IP dari reverse proxy lokal yang dipercaya untuk membaca header forwarding (`CF-Connecting-IP` dari Cloudflare atau `X-Forwarded-For` dari Caddy/Nginx).
   - Nilai `127.0.0.1` (default): Sangat ideal untuk Caddy, Nginx, atau daemon `cloudflared` yang berjalan di satu server fisik/VPS yang sama dengan Uvicorn.
   - Memastikan kuota rate limiter (60 request/menit) dihitung berdasarkan IP asli pengunjung luar secara adil, serta mencegah pihak luar memalsukan header IP palsu.

---

## 2. Jalur A: Reverse Proxy dengan Caddy (Paling Mudah)

Caddy secara otomatis mengurus penerbitan sertifikat SSL Let's Encrypt dan HTTP-to-HTTPS redirect.

### Langkah-langkah:
1. Pasang Caddy di server Linux (jika belum ada):
   ```bash
   sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
   sudo apt update && sudo apt install caddy
   ```

2. Tambahkan blok berikut ke `/etc/caddy/Caddyfile` (lihat `templates/Caddyfile.example`):
   ```caddy
   api.example.com {
       reverse_proxy 127.0.0.1:8300 {
           header_up Host {upstream_hostport}
           header_up X-Real-IP {remote_host}
           header_up X-Forwarded-For {remote_host}
           header_up X-Forwarded-Proto {scheme}
       }
   }
   ```

3. Muat ulang konfigurasi Caddy:
   ```bash
   sudo systemctl reload caddy
   ```

---

## 3. Jalur B: Cloudflare Tunnel (Tanpa Buka Port / Zero-Trust)

Cloudflare Tunnel (`cloudflared`) menghubungkan server lokal Anda ke jaringan edge Cloudflare melalui koneksi keluar (outbound), sehingga server tidak memerlukan IP publik atau port terbuka di firewall.

### Langkah-langkah:
1. Pasang `cloudflared`:
   ```bash
   curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared.deb
   ```

2. Autentikasi ke akun Cloudflare:
   ```bash
   cloudflared tunnel login
   ```

3. Buat Tunnel baru:
   ```bash
   cloudflared tunnel create ubsi-api-tunnel
   ```

4. Buat berkas konfigurasi `~/.cloudflared/config.yml` (lihat `templates/cloudflared.example.yml`):
   ```yaml
   tunnel: <TUNNEL_UUID>
   credentials-file: /home/ubuntu/.cloudflared/<TUNNEL_UUID>.json

   ingress:
     - hostname: api.example.com
       service: http://127.0.0.1:8300
     - service: http_status:404
   ```

5. Hubungkan domain di DNS Cloudflare:
   ```bash
   cloudflared tunnel route dns ubsi-api-tunnel api.example.com
   ```

6. Jalankan tunnel sebagai background service:
   ```bash
   sudo cloudflared service install
   sudo systemctl start cloudflared
   ```

---

## 4. Cara Memanggil Endpoint Terproteksi

Setelah domain aktif dengan HTTPS, seluruh endpoint privat wajib menyertakan header `X-API-Key`.

### Contoh cURL:

#### a. Health Check (Tanpa API Key — Selalu Terbuka)
```bash
curl -i https://api.example.com/health
```
Respons:
```json
{"status": "ok", "redis": "up"}
```

#### b. Request Tanpa Key (Ditolak 401)
```bash
curl -i https://api.example.com/v1/news
```
Respons:
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Akses ditolak: Header X-API-Key tidak valid atau tidak disertakan",
    "module": "auth"
  }
}
```

#### c. Request dengan Key Valid (Lolos 200 OK)
```bash
curl -i -H "X-API-Key: ubsi_sec_xxxxxxxxxxxxxxxx" https://api.example.com/v1/news
```

#### d. Mengambil Jadwal Kuliah Mahasiswa
```bash
curl -i -H "X-API-Key: ubsi_sec_xxxxxxxxxxxxxxxx" https://api.example.com/v1/studentv2/schedule
```

---

## 5. Ringkasan Keamanan Arsitektur

| Lapisan | Mekanisme | Manfaat |
|---|---|---|
| **Koneksi Jaringan** | TLS 1.3 / HTTPS Otomatis | Enkripsi data transit ujung-ke-ujung |
| **Bound Host** | `127.0.0.1` (Localhost) | Server port 8300 tidak bisa discan langsung dari internet |
| **Autentikasi** | `X-API-Key` constant-time | Mencegah akses liar & mitigasi serangan timing attack |
| **Rate Limiter** | Real Client IP Resolver | Kuota 60 req/menit bekerja adil per pengguna publik |
| **Upstream Protection** | Redis Caching 2-Tingkat + LGG | Mencegah spam atau overload ke server kampus UBSI |
