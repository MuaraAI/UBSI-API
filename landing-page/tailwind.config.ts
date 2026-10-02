import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#eef1f6",
        surface: "rgba(255, 255, 255, 0.60)",
        "surface-solid": "#ffffff",
        stroke: "rgba(17, 24, 39, 0.08)",
        foreground: "#1a1d26",
        secondary: "#5a616e",
        accent: {
          DEFAULT: "#92EEFF",
          hover: "#B8F5FF",
          dark: "#062535",
          muted: "rgba(146, 238, 255, 0.15)",
          glow: "rgba(146, 238, 255, 0.40)",
        },
        glass: {
          DEFAULT: "rgba(255, 255, 255, 0.60)",
          hover: "rgba(255, 255, 255, 0.80)",
          border: "rgba(255, 255, 255, 0.85)",
          strong: "rgba(255, 255, 255, 0.92)",
        },
        code: {
          bg: "#131b26",
          text: "#cdd6f4",
        },
      },
      fontFamily: {
        sans: ["var(--font-gordita)", "var(--font-inter)", "system-ui", "-apple-system", "sans-serif"],
        display: ["var(--font-gordita)", "var(--font-inter)", "system-ui", "-apple-system", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
        anton: ["var(--font-anton)", "Impact", "sans-serif"],
      },
      backdropBlur: {
        glass: "24px",
        "3xl": "48px",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(26, 58, 92, 0.06)",
        "glass-lg": "0 24px 48px rgba(26, 58, 92, 0.10)",
        "glass-xl": "0 36px 64px rgba(26, 58, 92, 0.14)",
        "glass-3d": "inset 0 1.5px 1px 0 rgba(255, 255, 255, 0.95), inset 0 -1px 2px 0 rgba(146, 238, 255, 0.25), 0 10px 30px -10px rgba(30, 41, 90, 0.12), 0 4px 12px -2px rgba(30, 41, 90, 0.06)",
        "glass-3d-hover": "inset 0 2px 4px 0 rgba(255, 255, 255, 1), inset 0 0 20px 0 rgba(146, 238, 255, 0.25), 0 20px 40px -10px rgba(146, 238, 255, 0.35), 0 10px 20px -5px rgba(26, 40, 70, 0.12)",
        "glass-edge": "inset 0 1px 0 rgba(255,255,255,0.9), inset 0 -1px 1px rgba(255,255,255,0.35)",
        float: "0 8px 32px rgba(146, 238, 255, 0.35)",
      },
      borderRadius: {
        sm: "12px",
        card: "18px",
        "card-3d": "20px",
        lg: "26px",
        pill: "100px",
      },
      transitionTimingFunction: {
        glass: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
