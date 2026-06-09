/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#002855",
          container: "#002855",
          fixed: "#d6e3ff",
          "fixed-dim": "#aac7fd",
          "on-container": "#7490c3",
          inverse: "#aac7fd",
        },
        secondary: {
          DEFAULT: "#334155",
          container: "#d5e3fd",
          "on-container": "#57657b",
        },
        tertiary: {
          DEFAULT: "#64748b",
        },
        surface: {
          DEFAULT: "#f7f9fb",
          dim: "#d8dadc",
          bright: "#f7f9fb",
          container: "#eceef0",
          "container-low": "#f2f4f6",
          "container-high": "#e6e8ea",
          "container-highest": "#e0e3e5",
          "container-lowest": "#ffffff",
        },
        "on-surface": {
          DEFAULT: "#191c1e",
          variant: "#43474f",
        },
        inverse: {
          surface: "#2d3133",
          "on-surface": "#eff1f3",
        },
        outline: {
          DEFAULT: "#747780",
          variant: "#c4c6d0",
        },
        error: {
          DEFAULT: "#ba1a1a",
          container: "#ffdad6",
          "on-container": "#93000a",
        },
        background: "#f7f9fb",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        "display-lg": ["32px", { lineHeight: "40px", fontWeight: "600", letterSpacing: "-0.02em" }],
        "headline-md": ["24px", { lineHeight: "32px", fontWeight: "600", letterSpacing: "-0.01em" }],
        "headline-sm": ["20px", { lineHeight: "28px", fontWeight: "500" }],
        "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "label-sm": ["12px", { lineHeight: "16px", fontWeight: "600", letterSpacing: "0.05em" }],
        "mono-code": ["13px", { lineHeight: "20px", fontWeight: "400" }],
      },
      spacing: {
        xs: "4px",
        sm: "8px",
        md: "16px",
        lg: "24px",
        xl: "32px",
        sidebar: "280px",
        gutter: "20px",
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
      },
      boxShadow: {
        kpi: "0px 4px 12px rgba(0, 40, 85, 0.05)",
      },
    },
  },
  plugins: [],
}
