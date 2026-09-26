# UBSI API

Private REST API aggregating UBSI student, LMS, library, and research services into structured JSON.

Personal automation backend for student bots and notification agents. Binds exclusively to localhost (`127.0.0.1:8300`).

---

> **PENTING / DISCLAIMER RESMI**:
>
> Proyek ini adalah **Unofficial API** independen yang dibuat semata-mata untuk tujuan riset edukasi, pembelajaran interoperabilitas perangkat lunak, dan mempermudah mahasiswa/developer UBSI mengakses data materi, jadwal, serta tugas perkuliahan milik mereka sendiri secara terstruktur tanpa perlu navigasi manual yang memakan waktu.
>
> **Batasan Tanggung Jawab**:
> 1. Proyek ini sama sekali **tidak berafiliasi resmi, tidak didukung, dan tidak dikelola oleh pihak Universitas Bina Sarana Informatika (UBSI)**.
> 2. Pembuat/maintainer repositori ini **tidak bertanggung jawab** atas segala bentuk penyalahgunaan, pelanggaran tata tertib, pemblokiran akun, atau kerugian apa pun yang diakibatkan oleh penggunaan tool ini. Penggunaan sepenuhnya menjadi risiko dan tanggung jawab masing-masing individu.
> 3. Semua merek dagang, nama sistem, materi silabus, dan data akademik adalah hak cipta dan kepemilikan penuh dari **Universitas Bina Sarana Informatika** serta pemilik hak ciptanya masing-masing.
>
> **Permohonan Penghapusan / Pengarsipan (Takedown Notice)**:
> Jika pihak otoritas universitas, pengelola sistem IT, atau dosen UBSI merasa keberatan atas keberadaan repositori ini, silakan hubungi maintainer langsung melalui GitHub ([@Curzyori](https://github.com/Curzyori)). Repositori ini akan dengan senang hati **diarsipkan, diubah, atau dihapus permanen secara kooperatif**.

---

## Why This

- **Two-tier Redis cache**: Tiered TTLs (schedules 2h, grades 30m, assignments 10m) with Last-Known-Good fallback (`stale: true`) when campus portals are down.
- **Anti-ban protection**: In-memory session cookie re-use, single-flight mutex per resource, and Chrome TLS fingerprint impersonation via Scrapling.
- **Normalized JSON**: Pervasive HTML cleanup; extracts clean integers, floats, ISO timestamps, and `null` values instead of raw table strings.
- **Local boundary**: Zero open ingress ports; private single-user deployment.

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Curzyori/UBSI-API.git
cd UBSI-API

# Virtual environment and dependencies (Python 3.12+)
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your student NIM/password

# Start local server
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8300
```

---

## Usage

Request active semester schedule:

```bash
curl -s http://127.0.0.1:8300/v1/studentv2/schedule | jq .
```

Real response payload:

```json
{
  "success": true,
  "data": [
    {
      "id": "e0a17f300c3b",
      "kode": "104",
      "nama": "BAHASA INGGRIS I",
      "hari": "Selasa",
      "jam": "09:10-10:50",
      "sks": 2,
      "kelompok_praktek": null,
      "ruang": "EN2-P1",
      "kode_dosen": "TDL"
    },
    {
      "id": "7b88ec7b6a12",
      "kode": "207",
      "nama": "LOGIKA DAN ALGORITMA",
      "hari": "Rabu",
      "jam": "08:20-11:40",
      "sks": 4,
      "kelompok_praktek": null,
      "ruang": "301-P1",
      "kode_dosen": "ERX"
    }
  ],
  "cached": false
}
```

Interactive OpenAPI documentation is available at `http://127.0.0.1:8300/docs`.

---

## Endpoints

| Service | Method | Route | Description |
|---|---|---|---|
| **System** | `GET` | `/health` | Server and Redis connectivity status |
| **StudentV2** | `GET` | `/v1/studentv2/schedule` | Active course schedule with room and lecturer |
| | `GET` | `/v1/studentv2/grades` | Semester grade breakdown (UTS, UAS, Tugas, Grade) |
| | `GET` | `/v1/studentv2/news` | Campus announcements archive |
| | `GET` | `/v1/studentv2/announcements` | Latest portal circulars (PDF links) |
| **Elearning** | `GET` | `/v1/elearning/courses` | LMS courses with encrypted action tokens |
| | `GET` | `/v1/elearning/assignments` | Active tasks and lecturer grading feedback |
| | `GET` | `/v1/elearning/presence` | Attendance logs per course meeting |
| | `GET` | `/v1/elearning/materials` | Download links for course syllabus and modules (ZIP) |
| | `GET` | `/v1/elearning/quiz` | Active online quizzes and practice exam schedules |
| **Elibrary** | `GET` | `/v1/elibrary/search` | OPAC library catalog search |
| | `GET` | `/v1/elibrary/book/{id}` | Book metadata, classification, and physical stock |
| **News** | `GET` | `/v1/news` | Official university news via WordPress REST API |
| | `GET` | `/v1/news/{id}` | Full article content and featured media |
| **Repository** | `GET` | `/v1/repository/recent` | Recent institutional research publications |
| | `GET` | `/v1/repository/search` | EPrints repository search |
| **EJournal** | `GET` | `/v1/ejournal/journals` | Catalog of 16 university academic journals |

---

## How It Works

<details>
<summary>Architecture & Upstream Request Lifecycle</summary>

```
Client Request -> Sliding Rate Limiter (Redis, 60 req/min)
               -> Cache Manager (Redis DB 2)
                    ├─ Fresh Cache Hit -> Return immediate JSON
                    └─ Cache Miss -> Scrapling Client (Chrome TLS impersonation)
                         ├─ In-memory cookie session -> Fetch upstream portal
                         ├─ If redirect to /login -> Auto re-login 1x & retry
                         ├─ Pure Parser -> Extract and sanitize data types
                         ├─ Save to Redis: fresh (tiered TTL) + LGG (no TTL)
                         └─ Return JSON
Upstream Error -> Check LGG in Redis -> Return cached data with stale: true
```

Scraping runs through Scrapling's `FetcherSession` with `impersonate="chrome"`, matching desktop browser TLS handshakes and headers.

</details>

---

## Testing & Deployment

- Run unit & integration tests:
  ```bash
  .venv/bin/pytest -v
  ```
- Run live smoke test suite:
  ```bash
  .venv/bin/python scripts/smoke.py --base-url http://127.0.0.1:8300
  ```
- Deploy to remote server via PM2:
  ```bash
  ./scripts/deploy.sh
  ```

---

## Documentation Links

- Contribution guidelines and test directory structure: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security policy and credential handling: [SECURITY.md](SECURITY.md)
- Intellectual property and copyright disclaimer: [DMCA.md](DMCA.md)
- License: [MIT License](LICENSE)
