# UBSI API – Design Specification (Glassmorphism v2)

## Overview

Light glassmorphism design system inspired by raflialdiansyah.com (Seeyaa77/portofolio).
White-dominant frosted glass surfaces over a soft blue-gray background with ambient color blobs.
Adapted for UBSI API with Ocean Cyan (#92EEFF) accent and Gordita font family.

## Color Palette

| Token              | Value                                              | Usage                        |
| ------------------ | -------------------------------------------------- | ---------------------------- |
| `--bg`             | `#eef1f6`                                          | Page background              |
| `--surface`        | `rgba(255, 255, 255, 0.60)`                        | Glass surface fill           |
| `--surface-solid`  | `#ffffff`                                          | Opaque surface               |
| `--stroke`         | `rgba(17, 24, 39, 0.08)`                           | Glass border                 |
| `--text`           | `#1a1d26`                                          | Primary text                 |
| `--text-muted`     | `#5a616e`                                          | Secondary text               |
| `--accent`         | `#92EEFF`                                          | Ocean Cyan accent            |
| `--accent-hover`   | `#B8F5FF`                                          | Accent hover                 |
| `--accent-dark`    | `#062535`                                          | Text on accent background    |
| `--code-bg`        | `#131b26`                                          | Dark code block background   |
| `--code-text`      | `#cdd6f4`                                          | Code text                    |

## Glass Tokens

| Property            | Value                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| Glass fill          | `linear-gradient(150deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.50) 45%, rgba(255,255,255,0.32) 100%)` |
| 3D Glass fill       | `linear-gradient(145deg, rgba(255,255,255,0.75) 0%, rgba(255,255,255,0.45) 50%, rgba(255,255,255,0.25) 100%)` |
| Backdrop filter     | `blur(24px) saturate(200%)`                                                                             |
| Glass stroke        | `1px solid rgba(255, 255, 255, 0.85)`                                                                   |
| Glass edge (inset)  | `inset 0 1.5px 1px 0 rgba(255,255,255,0.95), inset 0 -1px 2px 0 rgba(146,238,255,0.25)`               |
| Glass 3D Hover      | `transform: translateY(-7px) scale(1.015); border-color: rgba(146,238,255,0.9); glow: 0 20px 45px rgba(146,238,255,0.38)` |

## Typography

| Role    | Font           | Weights                        |
| ------- | -------------- | ------------------------------ |
| Body    | Gordita        | 400 (Regular), 500 (Medium)    |
| Display | Gordita        | 700 (Bold), 900 (Black)        |
| Code    | JetBrains Mono | 400, 500, 700                  |
| Fallback| Inter          | 400, 500, 600, 700             |

## Radius

| Size    | Value  |
| ------- | ------ |
| Small   | 12px   |
| Card    | 18px   |
| Large   | 26px   |
| Pill    | 100px  |

## Easing

`cubic-bezier(0.22, 1, 0.36, 1)` — all transitions.

## Background

- Base: `#eef1f6`
- Ambient blobs: teal (`#2DD4BF` at 15% opacity), indigo (`#818cf8` at 10%), pink (`#f472b6` at 8%)
- Grid overlay: 1px lines at 3% opacity

## Component Patterns

- **Navbar**: Floating pill, glass fill, centered within `max-w-5xl`, `border-radius: 100px`
- **Cards**: Glass fill + stroke + backdrop blur, `border-radius: 18px`, `padding: 24–32px`
- **Badges**: Accent bg at 10% opacity, accent text, `border-radius: 100px`
- **Code blocks**: Dark (`#1e1e2e`) inside glass container, `border-radius: 12px`
- **Buttons**: Primary = solid accent, Secondary = glass fill

## Accessibility

- All text pairs ≥ WCAG AA contrast (4.5:1)
- Focus: 2px solid accent outline with 2px offset
- `prefers-reduced-motion`: disable all animations
- Touch targets minimum 44×44px

## Voice & Tone

Technical, clean, developer-first. Indonesian for community content, English for labels.
No hype words — the API speaks for itself.
