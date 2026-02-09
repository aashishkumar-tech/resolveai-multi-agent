/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#070A12",
        card: "rgba(255, 255, 255, 0.06)",
        "card-border": "rgba(255, 255, 255, 0.10)",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(255,255,255,0.08), 0 12px 40px rgba(0,0,0,0.45)",
      },
    },
  },
  plugins: [],
};

