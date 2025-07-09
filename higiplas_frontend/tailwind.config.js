/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class', 
  theme: {
    extend: {
      colors: {
        'higiplas-blue': {
          DEFAULT: '#0054a6',
          50: '#e6f0fa',
          100: '#c0d4f5',
          200: '#8bb5ef',
          300: '#5796e9',
          400: '#2e7de3',
          500: '#0054a6',
          600: '#00468a',
          700: '#00366b',
          800: '#00264c',
          900: '#00172d',
        },
        'neutral-gray': {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
          darkBg: '#121212',
          darkSurface: '#1e1e1e',
          darkTextPrimary: '#e0e0e0',
          darkTextSecondary: '#a0a0a0',
          darkBorder: '#333333',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(0, 0, 0, 0.5)',
        'soft-md': '0 4px 12px rgba(0, 0, 0, 0.6)',
        'blue-glow': '0 0 8px rgba(0, 84, 166, 0.8)',
      },
      borderRadius: {
        'lg': '0.75rem',
        'xl': '1rem',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '26': '6.5rem',
      },
      transitionTimingFunction: {
        'in-expo': 'cubic-bezier(0.95, 0.05, 0.795, 0.035)',
      },
      animation: {
        fadeIn: 'fadeIn 0.5s ease forwards',
        slideUp: 'slideUp 0.4s ease forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
      },
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '2rem',
          lg: '4rem',
          xl: '5rem',
          '2xl': '6rem',
        },
        screens: {
          sm: '640px',
          md: '768px',
          lg: '1024px',
          xl: '1280px',
          '2xl': '1536px',
        },
      },
    },
  },
  plugins: [
  require('@tailwindcss/typography')
],
};

module.exports = config;