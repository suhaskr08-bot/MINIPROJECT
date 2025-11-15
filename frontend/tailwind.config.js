/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'insta-pink': '#E1306C',
        'insta-purple': '#C13584',
        'insta-blue': '#405DE6',
      },
    },
  },
  plugins: [],
}
