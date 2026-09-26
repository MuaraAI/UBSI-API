# Panduan Remote Access & Deployment Domain (UBSI API v1.1)

UBSI API dirancang dengan prinsip **Localhost-Only Security Boundary**: aplikasi berjalan murni di `127.0.0.1:8300` dan tidak pernah mengekspos port aplikasi secara langsung ke `0.0.0.0` publik.

Untuk mengakses API dari luar (aplikasi mobile, dashboard web, atau bot eksternal), tersedia dua jalur yang didukung secara resmi:
1. **Jalur A: Reverse Proxy (Caddy / Nginx)** — Direkomendasikan untuk VPS ber-IP publik.
2. **Jalur B: Cloudflare Tunnel (`cloudflared`)** — Direkomendasikan untuk laptop / homelab / VPS tanpa port publik (di balik CGNAT).

Semua akses remote diwajibkan menyertakan header keamanan **`X-API-Key`**.

---

## 1. Persiapan Kunci Akses (`API_KEY`)

Sebelum membuka akses remote, pastikan variabel `API_KEY` sudah terpasang di berkas `.env` server:

```bash
# Generate kunci rahasia 48 karakter acak:
python3 -c "import secrets; print('ubsi_sec_' + secrets.token_hex(24))"
```

Tempelkan ke berkas `.env`:
```bash
API_KEY=ubsi_sec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **Catatan Keamanan**: UBSI API menerapkan fail-fast startup. Jika `API_KEY` belum disetel, aplikasi akan menolak berjalan demi mencegah kebocoran data.

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
