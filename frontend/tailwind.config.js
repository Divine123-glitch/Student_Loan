/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'claude-bg': '#1e1e1e',
        'claude-sidebar': '#2d2d2d',
      }
    },
  },
  plugins: [],
}