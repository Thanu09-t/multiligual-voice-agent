/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Times New Roman"', 'Times', 'Georgia', 'Cambria', 'serif'],
      },
      colors: {
        border: "#E5E1DC",
        input: "#E5E1DC",
        ring: "#5A3828",
        background: "#F6F7F9",
        foreground: "#2B1810",
        chocolate: {
          DEFAULT: "#2B1810",
          dark: "#1A0E0A",
          medium: "#45281C",
          light: "#6E4532",
          muted: "#8C6552",
        },
        primary: {
          DEFAULT: "#2B1810",
          subtle: "rgba(43, 24, 16, 0.08)",
          border: "rgba(43, 24, 16, 0.18)",
        },
        accent: {
          bronze: "#9A6B43",
          emerald: "#166534",
          amber: "#B45309",
          rose: "#9F1239",
          slate: "#64748B",
        },
        nova: {
          bg: "#F6F7F9",
          surface: "#FFFFFF",
          card: "rgba(255, 255, 255, 0.92)",
          border: "#E5E1DC",
          subtle: "#8C6552",
        }
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow": "spin 12s linear infinite",
      }
    },
  },
  plugins: [],
};
