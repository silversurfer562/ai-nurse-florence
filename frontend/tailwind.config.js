/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./frontend/src/**/*.{html,js,jsx,ts,tsx}",
    "./frontend-react/src/**/*.{html,js,jsx,ts,tsx}",
    "./static/**/*.{html,js}",
    "./templates/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        // Healthcare Brand Colors
        clinical: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // Medical Status Colors
        medical: {
          'normal': '#10b981',    // Green - normal values
          'caution': '#f59e0b',   // Amber - caution required
          'warning': '#ef4444',   // Red - immediate attention
          'info': '#3b82f6',      // Blue - informational
          'critical': '#dc2626',  // Dark red - critical
        },
        // Clinical Roles
        nurse: {
          'primary': '#6366f1',   // Indigo - RN
          'advanced': '#8b5cf6',  // Purple - NP/CNS
          'admin': '#059669',     // Emerald - Nurse Admin
        }
      },
      fontFamily: {
        'clinical': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Courier New', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounce 2s infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        }
      },
      boxShadow: {
        'clinical': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'clinical-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'urgent': '0 0 0 3px rgba(239, 68, 68, 0.1), 0 4px 6px -1px rgba(239, 68, 68, 0.1)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    function({ addComponents, theme }) {
      addComponents({
        '.clinical-card': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.lg'),
          boxShadow: theme('boxShadow.clinical'),
          padding: theme('spacing.6'),
          borderLeft: `4px solid ${theme('colors.clinical.500')}`,
        },
        '.clinical-card-urgent': {
          borderLeftColor: theme('colors.medical.warning'),
          backgroundColor: theme('colors.red.50'),
          boxShadow: theme('boxShadow.urgent'),
        },
        '.clinical-card-success': {
          borderLeftColor: theme('colors.medical.normal'),
          backgroundColor: theme('colors.green.50'),
        },
        '.clinical-badge': {
          display: 'inline-flex',
          alignItems: 'center',
          padding: `${theme('spacing.1')} ${theme('spacing.2')}`,
          fontSize: theme('fontSize.xs'),
          fontWeight: theme('fontWeight.semibold'),
          borderRadius: theme('borderRadius.full'),
        },
        '.clinical-badge-normal': {
          backgroundColor: theme('colors.green.100'),
          color: theme('colors.green.800'),
        },
        '.clinical-badge-caution': {
          backgroundColor: theme('colors.yellow.100'),
          color: theme('colors.yellow.800'),
        },
        '.clinical-badge-warning': {
          backgroundColor: theme('colors.red.100'),
          color: theme('colors.red.800'),
        },
        '.wizard-progress': {
          height: theme('spacing.2'),
          backgroundColor: theme('colors.gray.200'),
          borderRadius: theme('borderRadius.full'),
          overflow: 'hidden',
        },
        '.wizard-progress-bar': {
          height: '100%',
          backgroundColor: theme('colors.clinical.500'),
          borderRadius: theme('borderRadius.full'),
          transition: 'width 0.3s ease',
        },
      })
    }
  ],
}
