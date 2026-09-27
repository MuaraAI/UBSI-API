# UBSI API Landing Page (`/web`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a high-performance, dark-first landing page for UBSI API in the monorepo `/web` directory using Next.js (App Router), Tailwind CSS, shadcn/ui primitives, and Anime.js, deployed to Vercel at `ubsi-api.muaraai.com`.

**Architecture:** Monorepo subdirectory `web/` with independent Next.js client/SSR setup. Self-hosted typography (Space Grotesk, Inter, JetBrains Mono) with zero external CDN dependencies. Live GitHub stats & health ping integration with static fallback resilience and edge-rendered dynamic OpenGraph images.

**Tech Stack:** Next.js 15+ (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui (Radix UI primitives), Anime.js (`animejs`), `@vercel/analytics`, `@vercel/og`.

**Spec:** `docs/superpowers/specs/2026-09-27-landing-page-web-design.md` & `web/DESIGN.md`.

## Global Constraints

- **Theme Palette:** Strictly adhere to Deep Water design tokens: Primary `#0A1220`, Surface `#111C2E`, Accent Teal `#2DD4BF`, Hover `#54E3D1`, Secondary Mist `#94A7BC`, Text `#E6EDF3`.
- **Zero Font/Asset CDNs:** All fonts must be copied from `/home/curzy/workspace/Fonts/Google/` and self-hosted via `next/font/local` in `web/public/fonts/`.
- **Zero Emoji in UI:** No emoji as icons, status indicators, bullets, or buttons; use inline Material Symbols Rounded or accessible SVG with `aria-hidden="true"`.
- **Environment Policy:** `NEXT_PUBLIC_API_URL` must not have a hardcoded fallback value; if unset, the health indicator defaults to standby without crashing.
- **Accessibility:** All text combinations must satisfy WCAG AA contrast (≥ 4.5:1). Keyboard focus rings must be visible (`outline: 2px solid #2DD4BF; outline-offset: 2px`). Respect `prefers-reduced-motion`.

## Review Focus

1. **Unset or Invalid `NEXT_PUBLIC_API_URL`:** Health probe fetch must catch network errors/timeouts gracefully and display a neutral standby chip without throwing unhandled runtime exceptions.
2. **GitHub API Rate Limiting or Private Repo State:** Server fetch for repo stars and contributor commit counts must fall back cleanly to static constants when GitHub API returns HTTP 403 or 404.
3. **Clipboard Copy Permissions:** Copy-to-clipboard functionality in CodeShowcase must handle non-HTTPS or denied navigator.clipboard permissions gracefully.
4. **Reduced Motion Accessibility:** Anime.js animations must check `window.matchMedia('(prefers-reduced-motion: reduce)')` and set duration to 0 or bypass transitions.
5. **Mobile Viewport Overflow (360px):** Code blocks and grid cards must utilize `overflow-x-auto` without breaking page container boundaries on narrow screens.

---

### Task 1: Next.js Workspace Scaffolding & Dependencies

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/next.config.ts`
- Create: `web/postcss.config.mjs`
- Create: `web/.gitignore`
- Assets: `web/public/fonts/*` (copied from `/home/curzy/workspace/Fonts/Google/`)

**Interfaces:**
- Consumes: Google Fonts `.woff2` files from `/home/curzy/workspace/Fonts/Google/`
- Produces: Base Next.js runtime environment in `web/`

- [ ] **Step 1: Create `web/package.json`**

```json
{
  "name": "ubsi-api-web",
  "version": "1.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --port 3000",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@radix-ui/react-slot": "^1.1.2",
    "@radix-ui/react-tabs": "^1.1.3",
    "@radix-ui/react-tooltip": "^1.1.8",
    "@vercel/analytics": "^1.5.0",
    "animejs": "^3.2.2",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.475.0",
    "next": "^15.1.7",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "tailwind-merge": "^3.0.1"
  },
  "devDependencies": {
    "@types/animejs": "^3.1.12",
    "@types/node": "^22.13.4",
    "@types/react": "^19.0.10",
    "@types/react-dom": "^19.0.4",
    "postcss": "^8.5.2",
    "tailwindcss": "^3.4.17",
    "typescript": "^5.7.3"
  }
}
```

- [ ] **Step 2: Create `web/tsconfig.json` and `web/next.config.ts`**

`web/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

`web/next.config.ts`:
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "github.com",
      },
    ],
  },
};

export default nextConfig;
```

`web/postcss.config.mjs`:
```javascript
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    tailwindcss: {},
  },
};

export default config;
```

`web/.gitignore`:
```
node_modules
.next
out
.DS_Store
*.pem
.env.local
.env.*.local
```

- [ ] **Step 3: Copy self-hosted fonts into `web/public/fonts/`**

Run:
```bash
mkdir -p web/public/fonts
cp /home/curzy/workspace/Fonts/Google/Space-Grotesk/SpaceGrotesk-SemiBold.woff2 web/public/fonts/
cp /home/curzy/workspace/Fonts/Google/Space-Grotesk/SpaceGrotesk-Bold.woff2 web/public/fonts/
cp /home/curzy/workspace/Fonts/Google/Inter/Inter-Regular.woff2 web/public/fonts/
cp /home/curzy/workspace/Fonts/Google/Inter/Inter-Medium.woff2 web/public/fonts/
cp /home/curzy/workspace/Fonts/Google/Inter/Inter-SemiBold.woff2 web/public/fonts/
cp /home/curzy/workspace/Fonts/Google/JetBrains-Mono/JetBrainsMono-Regular.woff2 web/public/fonts/
cp /home/curzy/workspace/Fonts/Google/JetBrains-Mono/JetBrainsMono-Medium.woff2 web/public/fonts/
```

- [ ] **Step 4: Install dependencies using npm**

Run: `cd web && npm install`
Expected: Dependencies installed, `web/package-lock.json` created.

- [ ] **Step 5: Commit scaffolding**

```bash
git add web/package.json web/package-lock.json web/tsconfig.json web/next.config.ts web/postcss.config.mjs web/.gitignore web/public/fonts
git commit -m "chore(web): scaffold next.js application with self-hosted google fonts"
```

---

### Task 2: Design Tokens, Tailwind & Global Layout

**Files:**
- Create: `web/tailwind.config.ts`
- Create: `web/src/app/globals.css`
- Create: `web/src/lib/utils.ts`
- Create: `web/src/app/layout.tsx`

**Interfaces:**
- Produces: `cn()` utility in `@/lib/utils`, theme CSS variables in `:root`, `@font-face` definitions in `src/app/layout.tsx`.

- [ ] **Step 1: Create `web/tailwind.config.ts`**

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A1220",
        surface: "#111C2E",
        "surface-hover": "#17263D",
        accent: {
          DEFAULT: "#2DD4BF",
          hover: "#54E3D1",
          dark: "#06251F",
        },
        secondary: "#94A7BC",
        foreground: "#E6EDF3",
        border: "rgba(255, 255, 255, 0.08)",
        ring: "#2DD4BF",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        display: ["var(--font-space-grotesk)", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      borderRadius: {
        sm: "4px",
        md: "8px",
        lg: "16px",
      },
      boxShadow: {
        float: "0 8px 24px rgba(2, 8, 20, 0.45)",
        glow: "0 0 20px rgba(45, 212, 191, 0.15)",
      },
    },
  },
  plugins: [],
};

export default config;
```

- [ ] **Step 2: Create `web/src/lib/utils.ts`**

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 3: Create `web/src/app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-primary: #0A1220;
  --color-surface: #111C2E;
  --color-accent: #2DD4BF;
  --color-accent-hover: #54E3D1;
  --color-text: #E6EDF3;
  --color-secondary: #94A7BC;
}

body {
  background-color: #0A1220;
  color: #E6EDF3;
  font-family: var(--font-inter), sans-serif;
  overflow-x: hidden;
  selection-background-color: #2DD4BF;
  selection-color: #06251F;
}

::selection {
  background-color: #2DD4BF;
  color: #06251F;
}

*:focus-visible {
  outline: 2px solid #2DD4BF;
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

- [ ] **Step 4: Create `web/src/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import localFont from "next/font/local";
import { Analytics } from "@vercel/analytics/react";
import "./globals.css";

const spaceGrotesk = localFont({
  src: [
    {
      path: "../../public/fonts/SpaceGrotesk-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "../../public/fonts/SpaceGrotesk-Bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-space-grotesk",
  display: "swap",
});

const inter = localFont({
  src: [
    {
      path: "../../public/fonts/Inter-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/Inter-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/Inter-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
  ],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = localFont({
  src: [
    {
      path: "../../public/fonts/JetBrainsMono-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/JetBrainsMono-Medium.woff2",
      weight: "500",
      style: "normal",
    },
  ],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "UBSI API — Unofficial REST API Aggregator 6 Layanan Kampus UBSI | Muara AI",
  description:
    "Agregator REST API modern untuk layanan Universitas Bina Sarana Informatika (SIAKAD, Elearning MyBest, E-Journal, E-Library, Repository, Berita). Caching Redis sub-250ms, open-source & developer-first.",
  keywords: [
    "UBSI API",
    "SIAKAD UBSI API",
    "Elearning MyBest UBSI",
    "Ejournal UBSI",
    "Muara AI",
    "API Kampus UBSI",
    "Yuken Velino",
    "Verzio",
  ],
  metadataBase: new URL("https://ubsi-api.muaraai.com"),
  alternates: {
    canonical: "https://ubsi-api.muaraai.com",
  },
  openGraph: {
    title: "UBSI API — Unofficial REST API Aggregator 6 Layanan Kampus UBSI",
    description:
      "Agregator data modern berkecepatan tinggi untuk SIAKAD, Elearning, Jurnal, E-Library, dan Repository UBSI.",
    url: "https://ubsi-api.muaraai.com",
    siteName: "UBSI API — Muara AI",
    locale: "id_ID",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "UBSI API — Unofficial REST API Aggregator 6 Layanan Kampus UBSI",
    description:
      "Agregator REST API modern untuk 6 layanan Universitas Bina Sarana Informatika.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": ["SoftwareApplication", "WebAPI"],
    name: "UBSI API",
    applicationCategory: "DeveloperApplication, EducationalApplication",
    operatingSystem: "Cloud, Docker, Linux",
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "IDR",
    },
    author: [
      {
        "@type": "Person",
        name: "Yuken Velino",
        url: "https://github.com/Curzyori",
      },
      {
        "@type": "Person",
        name: "Verzio",
        url: "https://github.com/MyKineID",
      },
    ],
    publisher: {
      "@type": "Organization",
      name: "Muara AI",
      url: "https://github.com/MuaraAI",
    },
  };

  return (
    <html
      lang="id"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="bg-background text-foreground antialiased min-h-screen">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

- [ ] **Step 5: Verify build with stub page**

Create temporary `web/src/app/page.tsx`:
```tsx
export default function Home() {
  return <div className="p-8 text-accent font-display text-3xl">UBSI API</div>;
}
```
Run: `cd web && npm run build`
Expected: Build passes with 0 errors.

- [ ] **Step 6: Commit theme and layout**

```bash
git add web/tailwind.config.ts web/src/lib/utils.ts web/src/app/globals.css web/src/app/layout.tsx web/src/app/page.tsx
git commit -m "feat(web): configure deep water theme tokens, self-hosted fonts, and root layout"
```

---

### Task 3: Static Data Layer & Realtime API Client

**Files:**
- Create: `web/src/types/index.ts`
- Create: `web/src/data/modules.ts`
- Create: `web/src/data/codeExamples.ts`
- Create: `web/src/data/contributors.ts`
- Create: `web/src/data/roadmap.ts`
- Create: `web/src/lib/github.ts`
- Create: `web/src/lib/health.ts`

**Interfaces:**
- Produces: `CAMPUS_MODULES`, `CODE_EXAMPLES`, `CONTRIBUTORS`, `ROADMAP_ITEMS`
- Produces: `getGitHubStats(): Promise<GitHubStats>`, `getHealthStatus(): Promise<HealthStatus>`

- [ ] **Step 1: Create `web/src/types/index.ts`**

```typescript
export interface CampusModule {
  id: string;
  name: string;
  service: string;
  description: string;
  endpointsCount: number;
  endpoints: string[];
  status: "Active" | "Cached" | "SWR";
}

export interface CodeExample {
  language: "curl" | "python" | "typescript";
  title: string;
  snippet: string;
  response: string;
  latencyMs: number;
}

export interface Contributor {
  name: string;
  username: string;
  role: string;
  nim: string;
  prodi: string;
  kelas: string;
  avatarUrl: string;
  profileUrl: string;
  fallbackCommits: number;
}

export interface RoadmapItem {
  version: string;
  title: string;
  description: string;
  badge: string;
  status: "upcoming" | "in-progress" | "planned";
}

export interface GitHubStats {
  stars: number;
  contributors: { [username: string]: number };
}

export interface HealthStatus {
  status: "ok" | "degraded" | "standby" | "down";
  redis: "up" | "down" | "unknown";
  latencyMs?: number;
}
```

- [ ] **Step 2: Create data files**

`web/src/data/modules.ts`:
```typescript
import { CampusModule } from "@/types";

export const CAMPUS_MODULES: CampusModule[] = [
  {
    id: "studentv2",
    name: "StudentV2 SIAKAD",
    service: "studentv2.bsi.ac.id",
    description: "Ekstraksi data akademik, jadwal perkuliahan, rincian KRS semester berjalan, KHS, dan rangkuman dashboard mahasiswa.",
    endpointsCount: 4,
    endpoints: ["/v1/studentv2/schedule", "/v1/studentv2/khs", "/v1/studentv2/krs", "/v1/studentv2/dashboard"],
    status: "Active",
  },
  {
    id: "elearning",
    name: "MyBest Elearning",
    service: "elearning.bsi.ac.id",
    description: "Parser kursus aktif, daftar tugas mingguan, materi kuliah perkuliahan, dan token autentikasi presensi terenkripsi.",
    endpointsCount: 4,
    endpoints: ["/v1/elearning/courses", "/v1/elearning/assignments", "/v1/elearning/materials", "/v1/elearning/schedule"],
    status: "Active",
  },
  {
    id: "ejournal",
    name: "E-Journal UBSI",
    service: "ejurnal.bsi.ac.id",
    description: "Katalog lengkap 23 jurnal resmi aktif kampus dengan judul asli, ISSN, dan direct link OJS volume/isu terbaru.",
    endpointsCount: 2,
    endpoints: ["/v1/ejournal/journals", "/v1/ejournal/articles"],
    status: "SWR",
  },
  {
    id: "elibrary",
    name: "E-Library Pustaka",
    service: "elibrary.bsi.ac.id",
    description: "Pencarian katalog koleksi perpustakaan, status ketersediaan buku fisik, nomor panggil, dan lokasi rak cabang kampus.",
    endpointsCount: 2,
    endpoints: ["/v1/elibrary/search", "/v1/elibrary/books/{id}"],
    status: "SWR",
  },
  {
    id: "repository",
    name: "Repository Karya Ilmiah",
    service: "repository.bsi.ac.id",
    description: "Publikasi tugas akhir, skripsi, dan riset sivitas akademika dengan penangkapan akurat URL rujukan /repo/{id}/.",
    endpointsCount: 2,
    endpoints: ["/v1/repository/recent", "/v1/repository/items/{id}"],
    status: "SWR",
  },
  {
    id: "news",
    name: "Campus News Portal",
    service: "news.bsi.ac.id",
    description: "Feed warta dan pengumuman resmi institusi UBSI secara real-time dengan kategori berita, tanggal, dan ringkasan.",
    endpointsCount: 2,
    endpoints: ["/v1/news/posts", "/v1/news/posts/{slug}"],
    status: "Active",
  },
];
```

`web/src/data/codeExamples.ts`:
```typescript
import { CodeExample } from "@/types";

export const CODE_EXAMPLES: Record<string, CodeExample> = {
  curl: {
    language: "curl",
    title: "cURL",
    snippet: `curl -X GET "https://ubsi-api.curzy.dev/v1/elearning/courses" \\
  -H "X-API-Key: ubsi_secret_key_anda" \\
  -H "Accept: application/json"`,
    response: `{
  "ok": true,
  "data": [
    {
      "code": "101",
      "name": "Dasar Manajemen Bisnis",
      "sks": 3,
      "lecturer": "Dr. Ir. Hendra S., M.Kom",
      "schedule": "Senin, 08:00 - 10:30 WIB",
      "assignments_pending": 0
    },
    {
      "code": "104",
      "name": "Logika & Algoritma",
      "sks": 4,
      "lecturer": "Ahmad Fauzi, M.Kom",
      "schedule": "Selasa, 10:30 - 13:00 WIB",
      "assignments_pending": 1
    },
    {
      "code": "153",
      "name": "Pengantar Teknologi Informasi",
      "sks": 3,
      "lecturer": "Budi Santoso, M.Kom",
      "schedule": "Rabu, 13:30 - 16:00 WIB",
      "assignments_pending": 0
    }
  ],
  "source": "cache",
  "fetched_at": "2026-09-27T10:15:30Z",
  "latency_ms": 238
}`,
    latencyMs: 238,
  },
  python: {
    language: "python",
    title: "Python (requests)",
    snippet: `import requests

headers = {
    "X-API-Key": "ubsi_secret_key_anda"
}

response = requests.get(
    "https://ubsi-api.curzy.dev/v1/elearning/courses", 
    headers=headers
)
data = response.json()
print(f"Total Kursus Aktif: {len(data['data'])}")`,
    response: `{
  "ok": true,
  "data": [
    {
      "code": "101",
      "name": "Dasar Manajemen Bisnis",
      "sks": 3,
      "lecturer": "Dr. Ir. Hendra S., M.Kom",
      "schedule": "Senin, 08:00 - 10:30 WIB"
    },
    {
      "code": "104",
      "name": "Logika & Algoritma",
      "sks": 4,
      "lecturer": "Ahmad Fauzi, M.Kom",
      "schedule": "Selasa, 10:30 - 13:00 WIB"
    }
  ],
  "source": "cache",
  "latency_ms": 242
}`,
    latencyMs: 242,
  },
  typescript: {
    language: "typescript",
    title: "TypeScript (fetch)",
    snippet: `const res = await fetch("https://ubsi-api.curzy.dev/v1/elearning/courses", {
  headers: {
    "X-API-Key": process.env.UBSI_API_KEY!
  },
  next: { revalidate: 60 }
});

const { data } = await res.json();
console.log(data);`,
    response: `{
  "ok": true,
  "data": [
    {
      "code": "101",
      "name": "Dasar Manajemen Bisnis",
      "sks": 3,
      "lecturer": "Dr. Ir. Hendra S., M.Kom",
      "schedule": "Senin, 08:00 - 10:30 WIB"
    }
  ],
  "source": "cache",
  "latency_ms": 229
}`,
    latencyMs: 229,
  },
};
```

`web/src/data/contributors.ts`:
```typescript
import { Contributor } from "@/types";

export const CONTRIBUTORS: Contributor[] = [
  {
    name: "Yuken Velino",
    username: "Curzyori",
    role: "Lead Maintainer & System Architect",
    nim: "15260767",
    prodi: "Informatika (S1)",
    kelas: "15.1C.30",
    avatarUrl: "https://github.com/Curzyori.png",
    profileUrl: "https://github.com/Curzyori",
    fallbackCommits: 28,
  },
  {
    name: "Verzio",
    username: "MyKineID",
    role: "Core Contributor & Endpoint Specialist",
    nim: "15260225",
    prodi: "Informatika (S1)",
    kelas: "15.1B.30",
    avatarUrl: "https://github.com/MyKineID.png",
    profileUrl: "https://github.com/MyKineID",
    fallbackCommits: 6,
  },
];
```

`web/src/data/roadmap.ts`:
```typescript
import { RoadmapItem } from "@/types";

export const ROADMAP_ITEMS: RoadmapItem[] = [
  {
    version: "v1.2",
    title: "Ekspor Kalender iCal (.ics)",
    description: "Sinkronisasi otomatis jadwal kuliah SIAKAD langsung ke Google Calendar di Android dan Apple Calendar di iOS.",
    badge: "Calendar Sync",
    status: "upcoming",
  },
  {
    version: "v1.2",
    title: "Rekap Nilai Tugas & Kuis Elearning",
    description: "Tracking status pengumpulan dan rekapitulasi nilai tugas 6 mata kuliah aktif per setiap pertemuan secara terstruktur.",
    badge: "Elearning Grades",
    status: "upcoming",
  },
  {
    version: "v1.2",
    title: "Bulk Modul Downloader",
    description: "Unduh seluruh berkas materi perkuliahan, slide presentasi, dan silabus 6 matkul sekaligus dalam satu file terkompresi.",
    badge: "Automation",
    status: "planned",
  },
  {
    version: "v1.2",
    title: "Kalkulator & Simulator IPK",
    description: "Simulasi perhitungan Indeks Prestasi Kumulatif berdasarkan riwayat nilai murni dan estimasi bobot nilai semester berjalan.",
    badge: "Productivity",
    status: "planned",
  },
];
```

- [ ] **Step 3: Create `web/src/lib/github.ts`**

```typescript
import { GitHubStats } from "@/types";

export async function getGitHubStats(): Promise<GitHubStats> {
  const defaultStats: GitHubStats = {
    stars: 2,
    contributors: {
      Curzyori: 28,
      MyKineID: 6,
    },
  };

  try {
    const [repoRes, contribRes] = await Promise.all([
      fetch("https://api.github.com/repos/MuaraAI/UBSI-API", {
        next: { revalidate: 3600 },
        headers: { Accept: "application/vnd.github.v3+json" },
      }),
      fetch("https://api.github.com/repos/MuaraAI/UBSI-API/contributors", {
        next: { revalidate: 3600 },
        headers: { Accept: "application/vnd.github.v3+json" },
      }),
    ]);

    if (!repoRes.ok || !contribRes.ok) {
      return defaultStats;
    }

    const repoData = await repoRes.json();
    const contribData = await contribRes.json();

    const contributorsMap: { [username: string]: number } = {};
    if (Array.isArray(contribData)) {
      contribData.forEach((c: { login: string; contributions: number }) => {
        contributorsMap[c.login] = c.contributions;
      });
    }

    return {
      stars: repoData.stargazers_count ?? defaultStats.stars,
      contributors: Object.keys(contributorsMap).length > 0 ? contributorsMap : defaultStats.contributors,
    };
  } catch {
    return defaultStats;
  }
}
```

- [ ] **Step 4: Create `web/src/lib/health.ts`**

```typescript
import { HealthStatus } from "@/types";

export async function checkApiHealth(): Promise<HealthStatus> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    return {
      status: "standby",
      redis: "unknown",
    };
  }

  const cleanUrl = apiUrl.replace(/\/+$/, "");
  const startTime = Date.now();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const res = await fetch(`${cleanUrl}/health`, {
      signal: controller.signal,
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    clearTimeout(timeoutId);

    const latencyMs = Date.now() - startTime;
    if (res.ok) {
      const data = await res.json();
      return {
        status: data.status === "ok" ? "ok" : "degraded",
        redis: data.redis === "up" ? "up" : "down",
        latencyMs,
      };
    }

    return {
      status: "degraded",
      redis: "unknown",
      latencyMs,
    };
  } catch {
    return {
      status: "down",
      redis: "unknown",
    };
  }
}
```

- [ ] **Step 5: Verify build with type checks**

Run: `cd web && npm run build`
Expected: Types and modules compile cleanly.

- [ ] **Step 6: Commit static data and api helpers**

```bash
git add web/src/types web/src/data web/src/lib/github.ts web/src/lib/health.ts
git commit -m "feat(web): add static datasets, github stats fetcher, and health probe utility"
```

---

### Task 4: Navbar & Live Health Badge Component

**Files:**
- Create: `web/src/components/Navbar.tsx`
- Create: `web/src/components/HealthBadge.tsx`
- Create: `web/src/components/Monogram.tsx`

**Interfaces:**
- Consumes: `HealthStatus` from `@/lib/health`
- Produces: `<Navbar starsCount={stars} />`

- [ ] **Step 1: Create `web/src/components/Monogram.tsx`**

```tsx
import React from "react";

export function Monogram({ className = "w-7 h-7" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <rect width="32" height="32" rx="6" fill="#111C2E" />
      {/* Wave flow left current */}
      <path
        d="M8 24V11L16 19L24 11V24"
        stroke="#2DD4BF"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="16" cy="19" r="1.5" fill="#54E3D1" />
    </svg>
  );
}
```

- [ ] **Step 2: Create `web/src/components/HealthBadge.tsx`**

```tsx
"use client";

import React, { useEffect, useState } from "react";
import { checkApiHealth } from "@/lib/health";
import { HealthStatus } from "@/types";

export function HealthBadge() {
  const [health, setHealth] = useState<HealthStatus>({
    status: "standby",
    redis: "unknown",
  });

  useEffect(() => {
    checkApiHealth().then(setHealth);
    const interval = setInterval(() => {
      checkApiHealth().then(setHealth);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  if (health.status === "ok") {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0A1220] border border-[#2DD4BF]/30 text-xs font-mono text-[#E6EDF3]">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span className="text-[#2DD4BF] font-semibold">LIVE v1.1.0</span>
        {health.latencyMs && (
          <span className="text-[#94A7BC] hidden sm:inline">({health.latencyMs}ms)</span>
        )}
      </div>
    );
  }

  if (health.status === "standby") {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0A1220] border border-white/10 text-xs font-mono text-[#94A7BC]">
        <span className="inline-flex rounded-full h-2 w-2 bg-[#94A7BC]"></span>
        <span>v1.1.0 STABLE</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0A1220] border border-amber-500/30 text-xs font-mono text-amber-300">
      <span className="inline-flex rounded-full h-2 w-2 bg-amber-400"></span>
      <span>CHECKING / OFFLINE</span>
    </div>
  );
}
```

- [ ] **Step 3: Create `web/src/components/Navbar.tsx`**

```tsx
import React from "react";
import Link from "next/link";
import { Monogram } from "./Monogram";
import { HealthBadge } from "./HealthBadge";

export function Navbar({ starsCount = 2 }: { starsCount?: number }) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0A1220]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group focus:outline-none">
          <Monogram className="w-8 h-8 group-hover:scale-105 transition-transform" />
          <div className="flex flex-col">
            <span className="font-display font-bold text-lg tracking-tight text-[#E6EDF3]">
              UBSI API
            </span>
            <span className="text-[10px] font-mono tracking-widest text-[#2DD4BF] uppercase -mt-1">
              Muara AI
            </span>
          </div>
        </Link>

        {/* Center Status */}
        <div className="hidden md:flex items-center">
          <HealthBadge />
        </div>

        {/* Navigation & Action */}
        <div className="flex items-center gap-4">
          <nav className="hidden lg:flex items-center gap-6 text-sm text-[#94A7BC]">
            <a href="#showcase" className="hover:text-[#E6EDF3] transition-colors">
              Showcase
            </a>
            <a href="#modules" className="hover:text-[#E6EDF3] transition-colors">
              Modul
            </a>
            <a href="#quickstart" className="hover:text-[#E6EDF3] transition-colors">
              Quickstart
            </a>
            <a href="#contributors" className="hover:text-[#E6EDF3] transition-colors">
              Kontributor
            </a>
          </nav>

          <a
            href="https://github.com/MuaraAI/UBSI-API"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#111C2E] hover:bg-[#17263D] border border-white/10 hover:border-[#2DD4BF]/40 text-xs font-mono text-[#E6EDF3] transition-all"
            aria-label="GitHub Repository"
          >
            <svg
              className="w-4 h-4 fill-current"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            <span className="font-semibold">Star</span>
            <span className="text-[#2DD4BF] font-bold">★ {starsCount}</span>
          </a>
        </div>
      </div>
    </header>
  );
}
```

- [ ] **Step 4: Verify build**

Run: `cd web && npm run build`
Expected: Navbar and components compile with zero errors.

- [ ] **Step 5: Commit Navbar and HealthBadge**

```bash
git add web/src/components/Monogram.tsx web/src/components/HealthBadge.tsx web/src/components/Navbar.tsx
git commit -m "feat(web): add navbar with live health badge, monogram, and github star indicator"
```

---

### Task 5: Hero Section Component with Anime.js Reveal

**Files:**
- Create: `web/src/components/Hero.tsx`

**Interfaces:**
- Produces: `<Hero />`

- [ ] **Step 1: Create `web/src/components/Hero.tsx`**

```tsx
"use client";

import React, { useEffect, useRef } from "react";
import anime from "animejs";

export function Hero() {
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    if (!prefersReducedMotion && heroRef.current) {
      anime({
        targets: heroRef.current.querySelectorAll(".anime-reveal"),
        opacity: [0, 1],
        translateY: [24, 0],
        delay: anime.stagger(120),
        duration: 800,
        easing: "cubicBezier(0.2, 0, 0, 1)",
      });
    }
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative pt-20 pb-16 md:pt-28 md:pb-24 px-4 sm:px-6 max-w-7xl mx-auto text-center flex flex-col items-center"
    >
      {/* Decorative background glow */}
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#2DD4BF]/10 rounded-full blur-3xl pointer-events-none -z-10"
        aria-hidden="true"
      />

      {/* Eyebrow */}
      <div className="anime-reveal inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-[#111C2E] border border-white/5 text-[11px] font-mono tracking-widest text-[#2DD4BF] uppercase mb-6">
        <span>UNOFFICIAL CAMPUS GATEWAY</span>
      </div>

      {/* H1 Heading */}
      <h1 className="anime-reveal font-display text-3xl sm:text-5xl md:text-6xl font-bold tracking-tight text-[#E6EDF3] max-w-4xl leading-[1.1] mb-6">
        Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.
      </h1>

      {/* Subtitle */}
      <p className="anime-reveal text-[#94A7BC] text-base sm:text-lg md:text-xl max-w-2xl leading-relaxed mb-10">
        Agregator data modern berkecepatan tinggi untuk SIAKAD, MyBest Elearning, E-Library,
        Repository, dan E-Journal dengan format JSON terstandarisasi dan Redis cache sub-250ms.
      </p>

      {/* CTA Buttons */}
      <div className="anime-reveal flex flex-wrap items-center justify-center gap-4 w-full sm:w-auto">
        <a
          href="#showcase"
          className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-md bg-[#2DD4BF] hover:bg-[#54E3D1] text-[#06251F] font-semibold text-sm transition-colors shadow-float"
        >
          Lihat Contoh Response
        </a>
        <a
          href="https://github.com/MuaraAI/UBSI-API"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-md bg-[#111C2E] hover:bg-[#17263D] text-[#E6EDF3] font-semibold text-sm border border-white/10 hover:border-[#2DD4BF]/50 transition-colors"
        >
          GitHub Repository
        </a>
      </div>

      {/* Trust & Architecture Pills */}
      <div className="anime-reveal mt-12 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono text-[#94A7BC]">
        <div className="px-4 py-2 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">6 Layanan</span> Terintegrasi
        </div>
        <div className="px-4 py-2 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">23 Jurnal</span> Aktif Resmi
        </div>
        <div className="px-4 py-2 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">Sub-250ms</span> Caching Latency
        </div>
        <div className="px-4 py-2 rounded-md bg-[#111C2E]/60 border border-white/5">
          <span className="text-[#2DD4BF] font-bold">71 Tests</span> 100% Passed
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npm run build`
Expected: Hero component compiles with 0 errors.

- [ ] **Step 3: Commit Hero section**

```bash
git add web/src/components/Hero.tsx
git commit -m "feat(web): add hero section with anime.js staggered reveal and call-to-actions"
```

---

### Task 6: Interactive Code Showcase Component

**Files:**
- Create: `web/src/components/CodeShowcase.tsx`

**Interfaces:**
- Consumes: `CODE_EXAMPLES` from `@/data/codeExamples`
- Produces: `<CodeShowcase />`

- [ ] **Step 1: Create `web/src/components/CodeShowcase.tsx`**

```tsx
"use client";

import React, { useState } from "react";
import { CODE_EXAMPLES } from "@/data/codeExamples";

export function CodeShowcase() {
  const [activeTab, setActiveTab] = useState<"curl" | "python" | "typescript">("curl");
  const [copied, setCopied] = useState(false);

  const activeExample = CODE_EXAMPLES[activeTab];

  const handleCopy = async () => {
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        await navigator.clipboard.writeText(activeExample.snippet);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // Fallback or silent fail for restricted environments
    }
  };

  return (
    <section id="showcase" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          DEVELOPER EXPERIENCE
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          Interaksi Cepat, Response Terstandarisasi.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Panggil data mata kuliah aktif MyBest Elearning secara langsung dengan header autentikasi terisolasi.
        </p>
      </div>

      {/* Terminal Window */}
      <div className="rounded-lg bg-[#111C2E] border border-white/10 shadow-float overflow-hidden">
        {/* macOS Window Title Bar */}
        <div className="flex items-center justify-between px-4 py-3 bg-[#0D1624] border-b border-white/5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#F87171]/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-[#FBBF24]/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-[#34D399]/80 inline-block" />
            <span className="text-xs font-mono text-[#94A7BC] ml-2 hidden sm:inline">
              GET /v1/elearning/courses
            </span>
          </div>

          {/* Language Selector Tabs */}
          <div className="flex items-center gap-1 bg-[#0A1220] p-1 rounded-md border border-white/5">
            {(["curl", "python", "typescript"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                  activeTab === tab
                    ? "bg-[#111C2E] text-[#2DD4BF] font-semibold"
                    : "text-[#94A7BC] hover:text-[#E6EDF3]"
                }`}
              >
                {tab === "curl" ? "cURL" : tab === "python" ? "Python" : "TypeScript"}
              </button>
            ))}
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#17263D] hover:bg-[#1C2F4C] text-xs font-mono text-[#E6EDF3] transition-colors border border-white/5"
            aria-label="Salin snippet kode"
          >
            <span>{copied ? "Disalin!" : "Salin"}</span>
          </button>
        </div>

        {/* Code & Response Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-white/5">
          {/* Left: Request Snippet */}
          <div className="p-4 sm:p-6 bg-[#0A1220]/60 overflow-x-auto">
            <div className="flex items-center justify-between text-xs font-mono text-[#94A7BC] mb-3">
              <span>REQUEST SNIPPET</span>
              <span className="text-[#2DD4BF]">X-API-Key: ••••••••</span>
            </div>
            <pre className="font-mono text-xs sm:text-sm text-[#E6EDF3] leading-relaxed whitespace-pre">
              <code>{activeExample.snippet}</code>
            </pre>
          </div>

          {/* Right: Response Payload */}
          <div className="p-4 sm:p-6 bg-[#111C2E] overflow-x-auto">
            <div className="flex items-center justify-between text-xs font-mono text-[#94A7BC] mb-3">
              <span>RESPONSE PAYLOAD (JSON)</span>
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 font-semibold">200 OK</span>
                <span className="text-[#94A7BC]">• {activeExample.latencyMs}ms</span>
              </div>
            </div>
            <pre className="font-mono text-xs text-[#94A7BC] leading-relaxed whitespace-pre max-h-[360px] overflow-y-auto">
              <code>{activeExample.response}</code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npm run build`
Expected: CodeShowcase compiles cleanly.

- [ ] **Step 3: Commit CodeShowcase**

```bash
git add web/src/components/CodeShowcase.tsx
git commit -m "feat(web): add interactive code showcase with elearning payload and copy action"
```

---

### Task 7: Campus Modules Grid & Architecture Metrics

**Files:**
- Create: `web/src/components/ModulesGrid.tsx`
- Create: `web/src/components/Architecture.tsx`

**Interfaces:**
- Consumes: `CAMPUS_MODULES` from `@/data/modules`
- Produces: `<ModulesGrid />`, `<Architecture />`

- [ ] **Step 1: Create `web/src/components/ModulesGrid.tsx`**

```tsx
import React from "react";
import { CAMPUS_MODULES } from "@/data/modules";

export function ModulesGrid() {
  return (
    <section id="modules" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          MODULAR ENDPOINTS
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          6 Layanan Kampus UBSI dalam Satu Standar.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-2xl mx-auto">
          Setiap modul dilengkapi isolasi parser, caching otomatis dua tingkat, dan mitigasi anti-blokir.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {CAMPUS_MODULES.map((mod) => (
          <div
            key={mod.id}
            className="rounded-lg bg-[#111C2E] border border-white/5 p-6 hover:border-[#2DD4BF]/40 transition-colors flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono text-[#2DD4BF] bg-[#0A1220] px-2.5 py-1 rounded border border-[#2DD4BF]/20">
                  {mod.endpointsCount} Endpoints
                </span>
                <span className="text-[11px] font-mono text-[#94A7BC]">
                  {mod.service}
                </span>
              </div>

              <h3 className="font-display text-lg font-semibold text-[#E6EDF3] group-hover:text-[#2DD4BF] transition-colors">
                {mod.name}
              </h3>
              <p className="text-xs sm:text-sm text-[#94A7BC] mt-2 leading-relaxed">
                {mod.description}
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-white/5">
              <span className="text-[11px] font-mono text-[#94A7BC] block mb-2">
                ENDPOINT UTAMA:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {mod.endpoints.slice(0, 2).map((ep) => (
                  <code
                    key={ep}
                    className="text-[10px] font-mono bg-[#0A1220] text-[#E6EDF3] px-2 py-0.5 rounded border border-white/5"
                  >
                    {ep}
                  </code>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Create `web/src/components/Architecture.tsx`**

```tsx
import React from "react";

export function Architecture() {
  const specs = [
    {
      title: "Redis SWR Caching",
      metric: "Sub-250ms",
      desc: "Caching dua tingkat (Redis DB 2) dengan latar belakang Stale-While-Revalidate untuk performa instant.",
    },
    {
      title: "Katalog OJS Lengkap",
      metric: "23 Jurnal",
      desc: "Penangkapan otomatis seluruh jurnal resmi aktif kampus dengan pemulihan judul murni dari server OJS.",
    },
    {
      title: "Headless Scrapling",
      metric: "Anti-Ban",
      desc: "Parser modern berbasis Scrapling v0.9+ dengan fingerprint Chrome TLS dan simulasi browser nyata.",
    },
    {
      title: "Zero-Secret Storage",
      metric: "Stateless",
      desc: "Tidak ada penyimpanan kredensial mahasiswa di basis data; otentikasi sesi terenkripsi penuh.",
    },
  ];

  return (
    <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="rounded-lg bg-[#0A1220] border border-white/10 p-8 sm:p-12">
        <div className="text-center mb-10">
          <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
            ENGINEERING EXCELLENCE
          </span>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
            Dibangun untuk Keandalan dan Kecepatan.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {specs.map((s, idx) => (
            <div
              key={idx}
              className="p-5 rounded-md bg-[#111C2E] border border-white/5 flex flex-col justify-between"
            >
              <div>
                <span className="font-display text-2xl font-bold text-[#2DD4BF]">
                  {s.metric}
                </span>
                <h3 className="font-display text-sm font-semibold text-[#E6EDF3] mt-1">
                  {s.title}
                </h3>
                <p className="text-xs text-[#94A7BC] mt-2 leading-relaxed">
                  {s.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Verify build**

Run: `cd web && npm run build`
Expected: ModulesGrid and Architecture compile cleanly.

- [ ] **Step 4: Commit ModulesGrid and Architecture**

```bash
git add web/src/components/ModulesGrid.tsx web/src/components/Architecture.tsx
git commit -m "feat(web): add campus modules 6-grid and engineering architecture specs"
```

---

### Task 8: Quickstart Guide & Contributors Section

**Files:**
- Create: `web/src/components/Quickstart.tsx`
- Create: `web/src/components/Contributors.tsx`

**Interfaces:**
- Consumes: `CONTRIBUTORS` from `@/data/contributors`
- Consumes: `stats` from `getGitHubStats()` in Task 3
- Produces: `<Quickstart />`, `<Contributors contributions={stats.contributors} />`

- [ ] **Step 1: Create `web/src/components/Quickstart.tsx`**

```tsx
import React from "react";

export function Quickstart() {
  return (
    <section id="quickstart" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          INSTALLATION IN 3 MINUTES
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          Jalankan Local Server UBSI API.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Ikuti panduan mudah 3 langkah untuk menjalankan backend aggregator di mesin Anda sendiri.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Step 1 */}
        <div className="rounded-lg bg-[#111C2E] border border-white/5 p-6 flex flex-col justify-between">
          <div>
            <span className="w-8 h-8 rounded-full bg-[#0A1220] border border-[#2DD4BF]/40 text-[#2DD4BF] font-mono text-sm font-bold flex items-center justify-center mb-4">
              1
            </span>
            <h3 className="font-display text-base font-semibold text-[#E6EDF3]">
              Clone & Setup Environment
            </h3>
            <p className="text-xs text-[#94A7BC] mt-2 mb-4 leading-relaxed">
              Unduh repositori resmi dan aktifkan virtual environment Python 3.10+.
            </p>
          </div>
          <pre className="p-3 rounded bg-[#0A1220] font-mono text-xs text-[#E6EDF3] overflow-x-auto border border-white/5">
            <code>{`git clone https://github.com/MuaraAI/UBSI-API.git
cd UBSI-API && python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt`}</code>
          </pre>
        </div>

        {/* Step 2 */}
        <div className="rounded-lg bg-[#111C2E] border border-white/5 p-6 flex flex-col justify-between">
          <div>
            <span className="w-8 h-8 rounded-full bg-[#0A1220] border border-[#2DD4BF]/40 text-[#2DD4BF] font-mono text-sm font-bold flex items-center justify-center mb-4">
              2
            </span>
            <h3 className="font-display text-base font-semibold text-[#E6EDF3]">
              Konfigurasi Berkas .env
            </h3>
            <p className="text-xs text-[#94A7BC] mt-2 mb-4 leading-relaxed">
              Salin contoh konfigurasi dan masukkan API Key serta kredensial akun SIAKAD.
            </p>
          </div>
          <pre className="p-3 rounded bg-[#0A1220] font-mono text-xs text-[#E6EDF3] overflow-x-auto border border-white/5">
            <code>{`cp .env.example .env
# Edit .env:
# API_KEY=kunci_rahasia_anda
# STUDENTV2_NIM=15260767
# STUDENTV2_PASS=password_anda`}</code>
          </pre>
        </div>

        {/* Step 3 */}
        <div className="rounded-lg bg-[#111C2E] border border-white/5 p-6 flex flex-col justify-between">
          <div>
            <span className="w-8 h-8 rounded-full bg-[#0A1220] border border-[#2DD4BF]/40 text-[#2DD4BF] font-mono text-sm font-bold flex items-center justify-center mb-4">
              3
            </span>
            <h3 className="font-display text-base font-semibold text-[#E6EDF3]">
              Jalankan Server Uvicorn
            </h3>
            <p className="text-xs text-[#94A7BC] mt-2 mb-4 leading-relaxed">
              Backend otomatis aktif pada port 8300 dengan dokumentasi Swagger interaktif.
            </p>
          </div>
          <pre className="p-3 rounded bg-[#0A1220] font-mono text-xs text-[#E6EDF3] overflow-x-auto border border-white/5">
            <code>{`uvicorn app.main:app --port 8300 --reload
# Buka Swagger UI:
# http://127.0.0.1:8300/docs`}</code>
          </pre>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Create `web/src/components/Contributors.tsx`**

```tsx
import React from "react";
import Image from "next/image";
import { CONTRIBUTORS } from "@/data/contributors";

export function Contributors({
  contributions = {},
}: {
  contributions?: { [username: string]: number };
}) {
  return (
    <section id="contributors" className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          OPEN SOURCE COLLABORATION
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          Dibangun oleh Mahasiswa, untuk Komunitas.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Dikembangkan secara independen oleh mahasiswa Informatika UBSI Pontianak di bawah naungan inisiatif Muara AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        {CONTRIBUTORS.map((c) => {
          const liveCommits = contributions[c.username] ?? c.fallbackCommits;

          return (
            <div
              key={c.username}
              className="rounded-lg bg-[#111C2E] border border-white/5 p-6 flex items-start gap-4 hover:border-[#2DD4BF]/40 transition-colors"
            >
              <Image
                src={c.avatarUrl}
                alt={c.name}
                width={64}
                height={64}
                className="rounded-full border border-[#2DD4BF]/30 shrink-0"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-display font-semibold text-base text-[#E6EDF3] truncate">
                    {c.name}
                  </h3>
                  <span className="text-xs font-mono text-[#2DD4BF] bg-[#0A1220] px-2 py-0.5 rounded border border-[#2DD4BF]/20">
                    {liveCommits} Commits
                  </span>
                </div>

                <a
                  href={c.profileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-mono text-[#94A7BC] hover:text-[#54E3D1] transition-colors block -mt-0.5"
                >
                  @{c.username}
                </a>

                <p className="text-xs font-medium text-[#2DD4BF] mt-2">
                  {c.role}
                </p>

                <div className="mt-2 text-[11px] font-mono text-[#94A7BC] leading-relaxed">
                  <div>Prodi: {c.prodi} • {c.kelas}</div>
                  <div>NIM: {c.nim}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 text-center">
        <a
          href="https://github.com/MuaraAI/UBSI-API/blob/main/CONTRIBUTING.md"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs font-mono text-[#94A7BC] hover:text-[#2DD4BF] underline underline-offset-4 transition-colors"
        >
          Ingin berkontribusi pada pengembangan UBSI API? Baca panduan di CONTRIBUTING.md →
        </a>
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Verify build**

Run: `cd web && npm run build`
Expected: Quickstart and Contributors compile cleanly.

- [ ] **Step 4: Commit Quickstart and Contributors**

```bash
git add web/src/components/Quickstart.tsx web/src/components/Contributors.tsx
git commit -m "feat(web): add 3-step quickstart guide and student contributors cards"
```

---

### Task 9: Roadmap Teaser & Footer Components

**Files:**
- Create: `web/src/components/RoadmapTeaser.tsx`
- Create: `web/src/components/Footer.tsx`

**Interfaces:**
- Consumes: `ROADMAP_ITEMS` from `@/data/roadmap`
- Produces: `<RoadmapTeaser />`, `<Footer />`

- [ ] **Step 1: Create `web/src/components/RoadmapTeaser.tsx`**

```tsx
import React from "react";
import { ROADMAP_ITEMS } from "@/data/roadmap";

export function RoadmapTeaser() {
  return (
    <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <span className="text-xs font-mono text-[#2DD4BF] tracking-widest uppercase">
          WHAT'S NEXT
        </span>
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-[#E6EDF3] mt-2">
          Roadmap v1.2 — Fitur Produktivitas Mahasiswa.
        </h2>
        <p className="text-[#94A7BC] text-sm sm:text-base mt-2 max-w-xl mx-auto">
          Fitur yang sedang dipersiapkan untuk memudahkan rutinitas perkuliahan harian.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {ROADMAP_ITEMS.map((item, idx) => (
          <div
            key={idx}
            className="rounded-lg bg-[#111C2E] border border-white/5 p-6 flex flex-col justify-between hover:border-[#2DD4BF]/30 transition-colors"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono font-bold text-[#2DD4BF] bg-[#0A1220] px-2 py-0.5 rounded border border-[#2DD4BF]/20 uppercase">
                  {item.badge}
                </span>
                <span className="text-xs font-mono text-[#94A7BC]">
                  {item.version}
                </span>
              </div>

              <h3 className="font-display text-base font-semibold text-[#E6EDF3]">
                {item.title}
              </h3>
              <p className="text-xs text-[#94A7BC] mt-2 leading-relaxed">
                {item.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-[#94A7BC]">
              <span>Status:</span>
              <span className="text-[#54E3D1] capitalize">{item.status}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Create `web/src/components/Footer.tsx`**

```tsx
import React from "react";
import { Monogram } from "./Monogram";

export function Footer() {
  return (
    <footer className="border-t border-white/5 bg-[#0D1624] py-12 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Brand & Monogram */}
        <div className="flex items-center gap-3">
          <Monogram className="w-8 h-8" />
          <div>
            <div className="font-display font-bold text-base text-[#E6EDF3]">
              UBSI API
            </div>
            <div className="text-xs font-mono text-[#94A7BC]">
              Muara AI — Deep Water: Local craft flows global.
            </div>
          </div>
        </div>

        {/* Legal Disclaimer */}
        <p className="text-[11px] font-mono text-[#94A7BC] text-center md:text-right max-w-md leading-relaxed">
          UBSI API adalah proyek riset independen non-komersial komunitas Muara AI dan tidak berafiliasi secara resmi dengan institusi Universitas Bina Sarana Informatika.
        </p>

        {/* Meta links */}
        <div className="flex items-center gap-4 text-xs font-mono text-[#94A7BC]">
          <span>MIT License</span>
          <span>•</span>
          <a
            href="https://github.com/MuaraAI/UBSI-API/releases"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-[#2DD4BF] transition-colors"
          >
            v1.1.0 Stable
          </a>
        </div>
      </div>
    </footer>
  );
}
```

- [ ] **Step 3: Verify build**

Run: `cd web && npm run build`
Expected: RoadmapTeaser and Footer compile cleanly.

- [ ] **Step 4: Commit RoadmapTeaser and Footer**

```bash
git add web/src/components/RoadmapTeaser.tsx web/src/components/Footer.tsx
git commit -m "feat(web): add roadmap v1.2 teaser and deep water footer with disclaimer"
```

---

### Task 10: Dynamic OpenGraph Image & Technical SEO Routing

**Files:**
- Create: `web/src/app/opengraph-image.tsx`
- Create: `web/src/app/sitemap.ts`
- Create: `web/src/app/robots.ts`

**Interfaces:**
- Produces: Dynamic `/opengraph-image` route via Next.js `ImageResponse`
- Produces: `/sitemap.xml`, `/robots.txt`

- [ ] **Step 1: Create `web/src/app/opengraph-image.tsx`**

```tsx
import { ImageResponse } from "next/og";

export const runtime = "edge";

export const alt = "UBSI API — Unofficial REST API Aggregator 6 Layanan Kampus UBSI";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "space-between",
          backgroundColor: "#0A1220",
          padding: "64px 80px",
          fontFamily: "sans-serif",
          border: "8px solid #111C2E",
        }}
      >
        {/* Top Header */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "48px",
              height: "48px",
              backgroundColor: "#111C2E",
              borderRadius: "10px",
              border: "2px solid #2DD4BF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#2DD4BF",
              fontSize: "24px",
              fontWeight: "bold",
            }}
          >
            M
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ color: "#E6EDF3", fontSize: "28px", fontWeight: "bold" }}>
              UBSI API
            </span>
            <span style={{ color: "#2DD4BF", fontSize: "14px", letterSpacing: "2px" }}>
              MUARA AI • DEEP WATER
            </span>
          </div>
        </div>

        {/* Center Content */}
        <div style={{ display: "flex", flexDirection: "column", maxWidth: "950px" }}>
          <span
            style={{
              color: "#E6EDF3",
              fontSize: "52px",
              fontWeight: 800,
              lineHeight: 1.15,
              marginBottom: "16px",
            }}
          >
            Satu Antarmuka REST API untuk Seluruh Layanan Kampus UBSI.
          </span>
          <span style={{ color: "#94A7BC", fontSize: "24px", lineHeight: 1.4 }}>
            SIAKAD • MyBest Elearning • E-Journal (23 Jurnal) • E-Library • Repository • News
          </span>
        </div>

        {/* Bottom Metrics Pill */}
        <div style={{ display: "flex", gap: "24px" }}>
          <div
            style={{
              backgroundColor: "#111C2E",
              padding: "10px 20px",
              borderRadius: "8px",
              color: "#2DD4BF",
              fontSize: "18px",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            Sub-250ms Redis Cache
          </div>
          <div
            style={{
              backgroundColor: "#111C2E",
              padding: "10px 20px",
              borderRadius: "8px",
              color: "#2DD4BF",
              fontSize: "18px",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            Open Source • MIT
          </div>
          <div
            style={{
              backgroundColor: "#111C2E",
              padding: "10px 20px",
              borderRadius: "8px",
              color: "#E6EDF3",
              fontSize: "18px",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            v1.1.0 Stable
          </div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
```

- [ ] **Step 2: Create `web/src/app/sitemap.ts` and `web/src/app/robots.ts`**

`web/src/app/sitemap.ts`:
```typescript
import { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: "https://ubsi-api.muaraai.com",
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1.0,
    },
  ];
}
```

`web/src/app/robots.ts`:
```typescript
import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: "https://ubsi-api.muaraai.com/sitemap.xml",
  };
}
```

- [ ] **Step 3: Verify build**

Run: `cd web && npm run build`
Expected: Static routes, sitemap, robots, and opengraph-image generate cleanly.

- [ ] **Step 4: Commit SEO files**

```bash
git add web/src/app/opengraph-image.tsx web/src/app/sitemap.ts web/src/app/robots.ts
git commit -m "feat(web): add dynamic edge opengraph image, sitemap, and robots routing"
```

---

### Task 11: Main Page Assembly & Production Build Verification

**Files:**
- Modify: `web/src/app/page.tsx`

**Interfaces:**
- Consumes: All components from `src/components/*` and `getGitHubStats()` from `src/lib/github`
- Produces: Complete production landing page.

- [ ] **Step 1: Assemble `web/src/app/page.tsx`**

```tsx
import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { CodeShowcase } from "@/components/CodeShowcase";
import { ModulesGrid } from "@/components/ModulesGrid";
import { Architecture } from "@/components/Architecture";
import { Quickstart } from "@/components/Quickstart";
import { Contributors } from "@/components/Contributors";
import { RoadmapTeaser } from "@/components/RoadmapTeaser";
import { Footer } from "@/components/Footer";
import { getGitHubStats } from "@/lib/github";

export const revalidate = 3600; // SWR cache at page root

export default async function Home() {
  const stats = await getGitHubStats();

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Navbar starsCount={stats.stars} />
      <main className="flex-1">
        <Hero />
        <CodeShowcase />
        <ModulesGrid />
        <Architecture />
        <Quickstart />
        <RoadmapTeaser />
        <Contributors contributions={stats.contributors} />
      </main>
      <Footer />
    </div>
  );
}
```

- [ ] **Step 2: Run complete production build in `web/`**

Run: `cd web && npm run build`
Expected output:
```
Route (app)                              Size     First Load JS
┌ ○ /                                    ... kB
├ ○ /_not-found                          ... kB
├ ƒ /opengraph-image                     ... B
├ ○ /robots.txt                          ... B
└ ○ /sitemap.xml                         ... B
+ First Load JS shared by all            ... kB

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand
```

- [ ] **Step 3: Verification check with test suite**

Run root pytest to ensure backend files are untouched:
Run: `pytest -q`
Expected: 71 passed.

- [ ] **Step 4: Commit assembled page**

```bash
git add web/src/app/page.tsx
git commit -m "feat(web): assemble complete landing page with live github stats and full section flow"
```

---

## Plan Self-Review Check

- **Spec coverage:** Checked — covers Next.js 15, React 19, Tailwind, shadcn/ui styling, Anime.js entrance animation, self-hosted fonts, 6 modules, code showcase with Elearning default, 3-step quickstart, contributors with live commits, roadmap v1.2 teaser, dynamic OG image, schema.org JSON-LD, and strict env policy.
- **Placeholder scan:** None — all code blocks are concrete and complete.
- **Type consistency:** All interfaces defined in `web/src/types/index.ts` match component usage across all tasks.
- **Review Focus:** Unset `NEXT_PUBLIC_API_URL` handled gracefully via `HealthBadge`, GitHub API rate limit handled via `getGitHubStats` fallback, reduced motion handled via media query checks, clipboard handled via try-catch, mobile container constrained via `max-w-7xl` and `overflow-x-auto`.
