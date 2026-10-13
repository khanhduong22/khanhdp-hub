/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './portfolio.html'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        zinc: {
          500: '#8e8e99', // WCAG AA compliant contrast ratio (>5.5:1 on dark)
        },
        craft: {
          bg: '#0a0a0a',
          card: '#121212',
          cardHover: '#171717',
          border: 'rgba(255, 255, 255, 0.08)',
          borderFocus: 'rgba(255, 255, 255, 0.18)',
          muted: '#8e8e99',
          text: '#f4f4f5',
          subtext: '#a1a1aa',
        },
        obsidian: {
          950: '#07080B',
          900: '#0E1015',
          850: '#111318',
          800: '#161922',
          700: '#222736',
          600: '#32394D',
        },
        amber: {
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
        },
        burgundy: {
          950: '#160208',
          900: '#230B14',
          850: '#2A0E19',
          800: '#3E1424',
          700: '#5C1A35',
        }
      }
    }
  }
};
