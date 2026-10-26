/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        civic: {
          navy: "#0f172a",
          slate: "#334155",
          teal: "#0d9488",
          amber: "#d97706",
          rose: "#e11d48",
          sky: "#0284c7",
          surface: "#f8fafc",
        }
      }
    },
  },
  plugins: [],
}
