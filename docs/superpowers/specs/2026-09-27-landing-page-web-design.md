# Design Specification: UBSI API Landing Page (`/web`)

**Date:** 2026-09-27  
**Status:** Validated & Ready for Planning  
**Target Domain:** `ubsi-api.muaraai.com` (Vercel)  
**Workspace Path:** `/home/curzy/workspace/Study/UBSI-API/web`  
**Identity Spec:** `web/DESIGN.md` (Muara AI — Deep Water)

---

## 1. Executive Summary & Goals

UBSI API is an unofficial REST API aggregator for 6 university web services of Universitas Bina Sarana Informatika (StudentV2 SIAKAD, MyBest Elearning, E-Journal, E-Library, Repository, and News). 

This project establishes the official landing page for the project inside the `/web` subdirectory of the monorepo `MuaraAI/UBSI-API`, deployed on Vercel under the subdomain `ubsi-api.muaraai.com`.

### Primary Objectives
1. **Showcase Capabilities:** Clearly present the 6 campus modules, 19+ endpoints, and sub-250ms response performance.
2. **Developer-First Experience:** Provide interactive copy-paste code snippets in cURL, Python, and TypeScript with real JSON response previews.
3. **Establish Community & Contributor Credibility:** Showcase the student builders (@Curzyori and @MyKineID) under the Muara AI initiative.
4. **Adhere to Deep Water Design Spec:** Implement the strict `web/DESIGN.md` design system (dark-first navy/teal, self-hosted typography, no emoji in UI, zero third-party CDN requests).

---

## 2. Technical Stack & Architecture

- **Framework:** Next.js (App Router, TypeScript)
- **Styling & Components:** 
  - Tailwind CSS configured with `web/DESIGN.md` Deep Water tokens.
  - **shadcn/ui** (Button, Card, Tabs, Badge, Tooltip) customized to dark-first Deep Water aesthetic (`#0A1220` background, `#111C2E` card/surface, `#2DD4BF` primary accent).
- **Animation Engine:** **Anime.js** (`animejs`)
  - Staggered entrance animation for Hero text and code block.
  - Number counter animation (0 → live stars, 0 → live commits, 0 → 198ms latency).
  - SVG path draw/flow animation for Muara Monogram "M" (representing "arus bertemu").
  - Tab switch smooth cross-fades.
  - Full respect for `prefers-reduced-motion` (disabled when requested by system).
- **Deployment:** Vercel (Monorepo setup: Root Directory set to `web`)
- **Font Strategy:** Self-hosted `.woff2` files copied from `/home/curzy/workspace/Fonts/Google/` into `web/public/fonts/` loaded via `next/font/local`:
  - Display/Heading: **Space Grotesk** (weights 600, 700)
  - Body & UI: **Inter** (weights 400, 500, 600)
  - Code & Eyebrows: **JetBrains Mono** (weights 400, 500)
- **Icons:** Material Symbols Rounded / inline accessible SVG with accessible titles (`aria-hidden="true"` for decorative icons). Strictly no emojis used as UI icons.

---

## 3. Directory & File Structure (`web/`)

```
web/
├── DESIGN.md
├── public/
│   ├── favicon.ico
│   ├── fonts/
│   │   ├── SpaceGrotesk-SemiBold.woff2
│   │   ├── SpaceGrotesk-Bold.woff2
│   │   ├── Inter-Regular.woff2
│   │   ├── Inter-Medium.woff2
│   │   ├── Inter-SemiBold.woff2
│   │   ├── JetBrainsMono-Regular.woff2
│   │   └── JetBrainsMono-Medium.woff2
│   └── images/
│       └── muara-monogram.svg
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── Hero.tsx
│   │   ├── CodeShowcase.tsx
│   │   ├── ModulesGrid.tsx
│   │   ├── Architecture.tsx
│   │   ├── Contributors.tsx
│   │   └── Footer.tsx
│   ├── data/
│   │   ├── modules.ts
│   │   ├── contributors.ts
│   │   └── codeExamples.ts
│   └── types/
│       └── index.ts
├── tailwind.config.ts
├── postcss.config.mjs
├── tsconfig.json
├── package.json
└── next.config.ts
```

---

## 4. UI/UX Section Specifications

### 4.1. Navbar (`Navbar.tsx`)
- **Sticky layout:** `h-16 border-b border-[#111C2E] bg-[#0A1220]/80 backdrop-blur-md px-6`
- **Left:** Muara Monogram SVG + brand text `UBSI API` (Space Grotesk 600).
- **Center:** Status Badge: `● LIVE v1.1.0` (Chip styling: JetBrains Mono 12px, green dot #34D399, bg-[#0A1220] border-[#111C2E]).
- **Right:** Navigation links (`Modul`, `Arsitektur`, `Kontributor`) + Secondary CTA to GitHub (`MuaraAI/UBSI-API`).

### 4.2. Hero Section (`Hero.tsx`)
- **Eyebrow:** `UNOFFICIAL CAMPUS GATEWAY` (JetBrains Mono 0.75rem, letter-spacing 0.08em, text-[#2DD4BF]).
- **H1 Heading:** `Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.` (Space Grotesk 3rem, weight 700, leading-tight, text-[#E6EDF3]).
- **Sub-headline:** `Agregator data real-time untuk SIAKAD, MyBest, E-Library, Repository, dan E-Journal dengan format JSON terstandarisasi dan Redis cache sub-250ms.` (Inter 1.125rem, text-[#94A7BC], max-w-2xl).
- **CTA Actions:**
  - `button-primary`: `Lihat Dokumentasi Endpoint` (bg-[#2DD4BF] text-[#06251F] hover:bg-[#54E3D1], px-6 py-3 rounded-md font-semibold).
  - `button-secondary`: `GitHub Repository` (bg-[#111C2E] text-[#E6EDF3] border border-white/10 hover:border-[#2DD4BF]/50 px-6 py-3 rounded-md font-semibold).

### 4.3. Interactive Code Showcase (`CodeShowcase.tsx`)
- **Layout:** Two-column split or stacked responsive card on `bg-[#111C2E]` surface with macOS window decoration (red/yellow/green pills).
- **Language Tabs:** `cURL`, `Python (requests)`, `TypeScript (fetch)`.
- **Left Panel (Request):** Syntax-highlighted code calling `GET /v1/studentv2/schedule` or `GET /v1/ejournal/journals` with `X-API-Key` headers.
- **Right Panel (Response):** Beautified real JSON payload with status `200 OK` badge and response time indicator (`~198ms`).
- **Interactive Action:** "Copy Snippet" button with feedback tooltip ("Disalin!").

### 4.4. Campus Services Grid (`ModulesGrid.tsx`)
Grid of 6 service cards (`bg-[#111C2E]`, rounded-lg, p-6, border border-white/5 hover:border-[#2DD4BF]/40 transition-colors):
1. **StudentV2 (SIAKAD):** Jadwal kuliah, nilai KHS, rincian KRS, dashboard semester. Tag: `4 Endpoints`.
2. **MyBest (Elearning):** Daftar kursus aktif, tugas mingguan, materi kuliah. Tag: `4 Endpoints`.
3. **E-Journal UBSI:** Katalog lengkap 23 jurnal resmi aktif & artikel OJS. Tag: `2 Endpoints`.
4. **E-Library:** Pencarian katalog buku, ketersediaan fisik, koleksi perpustakaan. Tag: `2 Endpoints`.
5. **Repository:** 15 publikasi karya ilmiah dan skripsi terbaru sivitas akademika. Tag: `2 Endpoints`.
6. **Campus News:** Feed portal berita resmi kampus secara real-time. Tag: `2 Endpoints`.

### 4.5. Engineering & Architecture (`Architecture.tsx`)
Highlighting backend reliability and speed:
- **Redis SWR Cache:** Sub-250ms latency with stale-while-revalidate background refresh.
- **Scrapling Engine:** Robust headless parsing overcoming dynamic DOM and OJS XML.
- **Zero-Secret Storage:** Encrypted session pooling with no persistent credential logging.
- **23 Official Journals:** Full OJS portal scraper capturing native academic publication titles.

### 4.6. Contributors Section (`Contributors.tsx`) & Realtime GitHub Stats
Headline: `Dibangun oleh Mahasiswa, untuk Komunitas.`  
Subtitle: `Dikembangkan secara independen oleh mahasiswa Informatika UBSI Pontianak di bawah inisiatif Muara AI.`
- **Realtime GitHub Stats Integration:**
  - Route handler / Server Component fetch ke GitHub REST API (`https://api.github.com/repos/MuaraAI/UBSI-API` dan `/contributors`) dengan `revalidate: 3600` (SWR caching).
  - Fallback data statis terpasang jika repo masih private atau rate-limit tercapai.
  - Total Stars live counter di Navbar & Hero button.
  - Realtime Commit counter di tiap kartu kontributor (`contributions` count dari GitHub API).
- **Card 1 — Yuken Velino (@Curzyori):**
  - Avatar: `https://github.com/Curzyori.png`
  - Role: Lead Maintainer & System Architect
  - Student Info: Informatika (S1), NIM 15260767, Kelas 15.1C.30
  - Live Metric: `{contributions} Commits` (Auto-synced via GitHub API)
  - GitHub Link: `https://github.com/Curzyori`
- **Card 2 — Verzio (@MyKineID):**
  - Avatar: `https://github.com/MyKineID.png`
  - Role: Core Contributor & Endpoint Specialist
  - Student Info: Informatika (S1), NIM 15260225, Kelas 15.1B.30
  - Live Metric: `{contributions} Commits` (Auto-synced via GitHub API)
  - GitHub Link: `https://github.com/MyKineID`
- **Contribution Callout:** `Ingin berkontribusi pada pengembangan UBSI API? Baca panduan di CONTRIBUTING.md.`

### 4.7. Quickstart & Installation Guide (`Quickstart.tsx`)
Section tutorial instalasi cepat 3 langkah untuk developer:
- **Step 1: Clone & Setup Virtual Environment**
  ```bash
  git clone https://github.com/MuaraAI/UBSI-API.git
  cd UBSI-API && python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  ```
- **Step 2: Konfigurasi `.env`**
  ```bash
  cp .env.example .env
  # Isi kredensial SIAKAD & Redis
  ```
- **Step 3: Jalankan Local Server**
  ```bash
  uvicorn app.main:app --port 8300 --reload
  ```
- **Link Dokumentasi Lengkap:**
  - Button ke Swagger Interactive UI (`https://ubsi-api.curzy.dev/docs`)
  - Link ke panduan Remote / Ingress (`docs/remote-access.md`)

### 4.8. Upcoming Roadmap Teaser v1.2 (`RoadmapTeaser.tsx`)
Grid card interaktif menampilkan fitur produktivitas yang sedang disiapkan:
1. 📅 **Ekspor Kalender iCal (`.ics`)**: Auto-sync jadwal kuliah langsung ke Google/Apple Calendar.
2. 📝 **Rekap Nilai Tugas & Kuis Elearning**: Tracking nilai tugas 6 mata kuliah aktif per setiap pertemuan.
3. 📦 **Bulk Downloader Materi Perkuliahan**: Unduh seluruh modul kuliah semester berjalan dalam 1 arsip zip.
4. 📊 **Simulator & Kalkulator IPK**: Simulasi target nilai dan predikat kelulusan mahasiswa.

### 4.9. Footer (`Footer.tsx`)
- Muara AI Monogram and tagline: *"Deep Water — Local craft flows global."*
- **Legal Disclaimer:** *"UBSI API adalah proyek riset independen non-komersial oleh komunitas Muara AI dan tidak berafiliasi secara resmi dengan Universitas Bina Sarana Informatika."*
- License: MIT License • Rilis v1.1.0.

---

## 5. SEO, Metadata, Accessibility & Performance

1. **OpenGraph & Social Cards:**
   - Title: `UBSI API — Unofficial REST API Aggregator 6 Layanan Kampus UBSI`
   - Description: `Agregator data modern berkecepatan tinggi untuk SIAKAD, Elearning, Jurnal, E-Library, dan Repository UBSI.`
   - Dynamic OG image matching Deep Water dark aesthetic.
2. **Live Health Ping:**
   - Real-time client polling/fetch ke `https://ubsi-api.curzy.dev/health` dengan dot indicator berkedip halus (pulse).
3. **WCAG AA Compliance:** All text combinations satisfy AA contrast (minimum 4.5:1 on dark surfaces). `#94A7BC` on `#0A1220` is 5.5:1. `#2DD4BF` on `#0A1220` is 9.8:1.
4. **Keyboard Navigation:** Explicit visible focus rings (`outline: 2px solid #2DD4BF; outline-offset: 2px`).
5. **Motion Safety:** All anime.js animations respect `prefers-reduced-motion: reduce`.
6. **Touch Target Size:** All buttons and interactive tabs have minimum dimensions of 44x44px.

---

## 6. Verification & Acceptance Criteria

1. `npm run build` inside `web/` completes with 0 errors and 0 type warnings.
2. Zero external CDN calls for fonts or styles (all fonts self-hosted in `public/fonts/`).
3. All interactive buttons (copy code, switch tabs) function seamlessly without layout shifts.
4. Fully responsive layout tested across mobile (360px), tablet (768px), and desktop (1280px).
