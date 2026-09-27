---
version: alpha
name: Muara AI — Deep Water
description: Dark-first builder identity — deep water navy with one luminous current. Local craft flows global.
colors:
  primary: "#0A1220"
  surface: "#111C2E"
  secondary: "#94A7BC"
  accent: "#2DD4BF"
  accent-hover: "#54E3D1"
  text: "#E6EDF3"
  success: "#34D399"
  warning: "#FBBF24"
  danger: "#F87171"
typography:
  h1:
    fontFamily: Space Grotesk
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h2:
    fontFamily: Space Grotesk
    fontSize: 2.25rem
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  h3:
    fontFamily: Space Grotesk
    fontSize: 1.5rem
    fontWeight: 600
    lineHeight: 1.25
  body-lg:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
  mono-label:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.08em"
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#06251F"
    rounded: "{rounded.md}"
    padding: 12px
    typography:
      fontFamily: Inter
      fontSize: 1rem
      fontWeight: 600
      lineHeight: 1.4
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
    textColor: "#06251F"
    rounded: "{rounded.md}"
    padding: 12px
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.lg}"
    padding: 24px
  input:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: 12px
  chip-status-success:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.success}"
    rounded: 999px
    padding: 4px
  chip-status-warning:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.warning}"
    rounded: 999px
    padding: 4px
  chip-status-danger:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.danger}"
    rounded: 999px
    padding: 4px
  eyebrow-label:
    textColor: "{colors.accent}"
    typography:
      fontFamily: JetBrains Mono
      fontSize: 0.75rem
      fontWeight: 500
      lineHeight: 1.4
      letterSpacing: "0.08em"
---

## Overview

Muara AI — komunitas praktisi AI dari Pontianak. Identitas visualnya "Deep Water": permukaan laut dalam (navy gelap) dengan satu arus bercahaya (teal) sebagai satu-satunya penggerak interaksi. Dark-first karena audiens intinya builder — screenshot kode, video, dan karya visual anggota pop di atas permukaan gelap ini. Sengaja menjauhi estetika AI default (gradient ungu-biru, pastel glassmorphism).

Satu momen gradien diizinkan: monogram/logo "M" (dua arus bertemu) — di mana pun itu, bukan sebagai pembawa identitas halaman.

## Colors

- **Primary #0A1220 (Deep Water):** background dasar seluruh halaman; juga tinta heading saat tampil di media inverse (deck light).
- **Surface #111C2E:** permukaan naik — kartu, panel, navigasi.
- **Secondary #94A7BC (Mist):** teks sekunder, meta, caption. Tetap lolos AA di atas primary.
- **Accent #2DD4BF (Arus):** satu-satunya warna interaksi — link, tombol utama, status aktif, label eyebrow. Kalau warna ini muncul di halaman, itu berarti sesuatu bisa diklik atau sedang aktif.
- **Text #E6EDF3:** teks utama di tema gelap.
- **Semantic:** success #34D399, warning #FBBF24, danger #F87171 — hanya untuk status, bukan dekorasi.

Semua pasangan teks di atas lolos WCAG AA (≥ 4.5:1) di atas permukaan gelapnya.

## Typography

Tiga keluarga, semua di-host sendiri (woff2 di `public/fonts/`, `font-display: swap`, tanpa CDN):

- **Space Grotesk** — display & heading (h1–h3). Geometris, sedikit teknis.
- **Inter** — body & UI (body-lg, body-md, caption). Netral, nyaman dibaca panjang.
- **JetBrains Mono** — label eyebrow all-caps, kode, dan angka metadata. Sinyal "builder".

Skala: 3rem / 2.25rem / 1.5rem / 1.125rem / 1rem / 0.875rem — jangan bikin ukuran di luar skala.

## Layout

- Container konten maksimum 72rem, terpusat, padding sisi minimal 16px (mobile) / 24px (desktop).
- Ritme spasi 8 / 16 / 24; section besar diberi napas 48px ke atas-bawah (2× lg).
- Grid member/karya: kartu 3 kolom (desktop) → 2 (md) → 1 (mobile), gap 24px.

## Elevation & Depth

Tema gelap: elevation pakai permukaan + bayangan lembut, bukan warna makin terang.

- Bayangan standar: `0 8px 24px rgba(2, 8, 20, 0.45)` — hanya untuk elemen mengambang (kartu profil saat hover, dropdown, modal).
- Permukaan biasa (kartu statis) cukup `surface` tanpa bayangan.

## Motion

Durasi: fast 150ms (hover, chip), base 250ms (panel, modal). Easing tunggal: `cubic-bezier(0.2, 0, 0, 1)`. Animasi identitas cuma satu momen: arus di logo/hero. `prefers-reduced-motion` mematikan semuanya.

## Breakpoints

sm 640px, md 768px, lg 1024px. Mobile-first — grid 1 kolom dasar, naik 2 lalu 3 sesuai Layout.

## Shapes

Radius kecil-kecil: sm 4px (input, tag), md 8px (tombol), lg 16px (kartu). Tidak ada pill penuh kecuali chip status. Sudut tajam-soft — bukan blob super-rounded.

## Components

- `button-primary` — aksi utama satu per layar. Teal dengan tinta gelap #06251F, kontras 8.7:1.
- `card` — kontainer standar member/karya/proyek di surface.
- `input` — form di atas primary, radius sm.
- `eyebrow-label` — label mono all-caps teal di atas heading section; identitas ritme tipografi khas Muara.

## Do's and Don'ts

Do:

- Teal hanya untuk interaksi dan status aktif.
- Background selalu primary/surface; foto & karya anggota diberi frame card.
- Font woff2 di-commit ke `public/fonts/` dari library lokal; tanpa Google Fonts CDN.
- Ikon: Material Symbols Rounded self-hosted, `aria-hidden` untuk dekoratif.

Don't:

- Jangan gradient ungu-biru, glassmorphism, atau glow neon berlebih — itu slop.
- Jangan pakai warna aksen kedua; kalau butuh hierarki, pakai ketebalan & ukuran.
- Jangan emoji sebagai ikon UI.
- Jangan teks abu-abu di bawah #94A7BC di atas gelap — gagal kontras.

## Voice & Tone

Tegas, teknis, sedikit puitis kalau bicara brand ("semua skill mengalir bertemu"). Bahasa Indonesia santai untuk komunitas internal; English untuk publikasi global & README. Tidak ada hype words ("revolutionary", "10x") — bukti karya bicara.

## Accessibility

- Kontras semua pasangan teks ≥ AA (terverifikasi lint).
- Fokus keyboard: outline 2px accent dengan offset 2px — jangan dihapus.
- `prefers-reduced-motion`: matikan animasi arus/parallax.
- Target sentuh minimal 44×44px.
