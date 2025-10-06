/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // AI Nurse Florence brand colors
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#991b1b',  // Main maroon
          600: '#800020',  // Classic maroon
          700: '#7f1d1d',
          800: '#6b1515',
          900: '#5a0f0f',
        },
        accent: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',  // Lighter gold
          500: '#d4af37',  // Classic gold
          600: '#b8860b',  // Dark goldenrod
          700: '#92700a',
          800: '#78590a',
          900: '#5c4508',
        },
        medical: {
          emergency: '#dc2626',  // Red for warnings/errors only
          urgent: '#f59e0b',
          routine: '#10b981',
          info: '#3b82f6',
        }
      },
    },
  },
  plugins: [],
}
