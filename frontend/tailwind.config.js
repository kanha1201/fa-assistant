/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'groww-black': '#121212',
        'groww-surface': '#1E1E1E',
        'groww-border': '#2C2C2E',
        'groww-chip': '#2A2A2A',
        'groww-chip-border': '#374151',
        'groww-mint': '#00D09C',
        'groww-coral': '#EB5B3C',
        'groww-white': '#FFFFFF',
        'groww-gray': '#9CA3AF',
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}


