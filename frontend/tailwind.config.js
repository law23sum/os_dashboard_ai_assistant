/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Tkinter-inspired theme colors (exact match from gui.py)
        osd: {
          background: 'var(--osd-background)',
          backgroundAlt: 'var(--osd-backgroundAlt)',
          surface: 'var(--osd-surface)',
          surfaceAlt: 'var(--osd-surfaceAlt)',
          border: 'var(--osd-border)',
          text: 'var(--osd-text)',
          muted: 'var(--osd-muted)',
          accent: 'var(--osd-accent)',
          accentHover: 'var(--osd-accentHover)',
          pill: 'var(--osd-pill)',
          success: 'var(--osd-success)',
          error: 'var(--osd-error)',
          warning: 'var(--osd-warning)',
          info: 'var(--osd-info)',
          primary: 'var(--osd-primary)',
          secondary: 'var(--osd-secondary)',
        },
        // Legacy primary colors for compatibility
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#6366f1', // Updated to match Tkinter accent
          600: '#4f46e5', // Updated to match Tkinter accentHover
          700: '#7c3aed', // Updated to match Tkinter accentHover dark
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}

