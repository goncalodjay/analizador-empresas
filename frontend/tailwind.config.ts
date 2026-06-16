import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f7ff",
          100: "#e0effe",
          200: "#c2e0fe",
          300: "#84cafd",
          400: "#41b6ff",
          500: "#0099ff",
          600: "#0066cc",
          700: "#0052a3",
          800: "#003d7a",
          900: "#002e5c",
        },
        success: "#00aa00",
        warning: "#ff8800",
        error: "#cc0000",
        neutral: {
          0: "#ffffff",
          50: "#f9fafb",
          100: "#f3f4f6",
          200: "#e5e7eb",
          300: "#d1d5db",
          400: "#9ca3af",
          500: "#6b7280",
          600: "#4b5563",
          700: "#374151",
          800: "#1f2937",
          900: "#111827",
        },
      },
      spacing: {
        xs: "4px",
        sm: "8px",
        md: "12px",
        lg: "16px",
        xl: "24px",
        "2xl": "32px",
      },
      fontSize: {
        xs: "12px",
        sm: "14px",
        base: "16px",
        lg: "18px",
        xl: "24px",
        "2xl": "32px",
      },
      fontWeight: {
        normal: "400",
        semibold: "600",
        bold: "700",
      },
      borderRadius: {
        sm: "4px",
        md: "8px",
        lg: "16px",
      },
      transitionDuration: {
        150: "150ms",
        300: "300ms",
      },
      transitionTimingFunction: {
        "ease-in": "ease-in",
        "ease-out": "ease-out",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "Segoe UI", "system-ui", "sans-serif"],
      },
      boxShadow: {
        subtle: "0 1px 2px 0 rgba(0,0,0,0.05)",
        medium: "0 4px 6px -1px rgba(0,0,0,0.1)",
        prominent: "0 20px 25px -5px rgba(0,0,0,0.1)",
      },
    },
  },
  plugins: [],
};

export default config;
