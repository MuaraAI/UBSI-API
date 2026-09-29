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
        surface: "rgba(255, 255, 255, 0.55)",
        "surface-solid": "#ffffff",
        stroke: "rgba(17, 24, 39, 0.08)",
        foreground: "#1a1d26",
        secondary: "#5a616e",
        accent: {
          DEFAULT: "#2DD4BF",
          hover: "#54E3D1",
          dark: "#06251F",
          muted: "rgba(45, 212, 191, 0.10)",
        },
        glass: {
          DEFAULT: "rgba(255, 255, 255, 0.55)",
          hover: "rgba(255, 255, 255, 0.72)",
          border: "rgba(17, 24, 39, 0.08)",
          strong: "rgba(255, 255, 255, 0.85)",
        },
        code: {
          bg: "#1e1e2e",
          text: "#cdd6f4",
        },
      },
      fontFamily: {
        sans: ["var(--font-gordita)", "var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-gordita)", "var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      backdropBlur: {
        glass: "22px",
        "3xl": "48px",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(26, 58, 92, 0.06)",
        "glass-lg": "0 24px 48px rgba(26, 58, 92, 0.10)",
        "glass-xl": "0 36px 64px rgba(26, 58, 92, 0.14)",
        "glass-edge": "inset 0 1px 0 rgba(255,255,255,0.9), inset 0 -1px 1px rgba(255,255,255,0.35)",
        float: "0 8px 32px rgba(26, 58, 92, 0.08)",
      },
      borderRadius: {
        sm: "12px",
        card: "18px",
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
