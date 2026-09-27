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
