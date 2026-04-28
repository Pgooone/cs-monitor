import { defineConfig, presetUno, presetIcons } from 'unocss'

export default defineConfig({
  presets: [presetUno(), presetIcons()],
  theme: {
    colors: {
      brand: {
        DEFAULT: '#6366f1',
        50: '#eef2ff',
        100: '#e0e7ff',
        200: '#c7d2fe',
        300: '#a5b4fc',
        400: '#818cf8',
        500: '#6366f1',
        600: '#4f46e5',
        700: '#4338ca',
        800: '#3730a3',
        900: '#312e81',
        950: '#1e1b4b',
      },
      bg: '#050505',
      surface: {
        DEFAULT: '#0f0f12',
        hover: '#16161d',
      },
      border: {
        DEFAULT: '#1f1f23',
        bright: '#2d2d35',
      },
      'on-bg': '#ffffff',
      'on-muted': '#94a3b8',
      rise: '#ef4444',
      fall: '#22c55e',
      up: 'var(--color-up, #ef4444)',
      down: 'var(--color-down, #22c55e)',
    },
    fontFamily: {
      sans: "'Inter', 'PingFang SC', 'Microsoft YaHei', 'HarmonyOS Sans', sans-serif",
      mono: "'JetBrains Mono', 'SF Mono', 'Fira Code', 'Cascadia Code', monospace",
      display: "'Inter', 'PingFang SC', sans-serif",
    },
    borderRadius: {
      xs: '0.1875rem',
      sm: '0.375rem',
      base: '0.5rem',
      md: '0.625rem',
      lg: '0.75rem',
      xl: '1rem',
      '2xl': '1.25rem',
      '3xl': '1.5rem',
      card: '1rem',
      modal: '1.25rem',
    },
    boxShadow: {
      xs: '0 1px 2px rgba(0,0,0,0.04)',
      sm: '0 1px 3px rgba(0,0,0,0.06)',
      md: '0 4px 8px rgba(0,0,0,0.08)',
      lg: '0 12px 24px rgba(0,0,0,0.12)',
      glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
      'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.4)',
      glow: '0 0 15px rgba(99, 102, 241, 0.4)',
      'glow-sm': '0 0 10px rgba(99, 102, 241, 0.2)',
    },
  },
  preflights: [
    {
      getCSS: () => `
        html {
          --color-up: #ef4444;
          --color-down: #22c55e;
        }
        html.dark {
          --color-up: #ef4444;
          --color-down: #22c55e;
        }
        html[data-rise-fall="international"] {
          --color-up: #22c55e;
          --color-down: #ef4444;
        }
        html.dark[data-rise-fall="international"] {
          --color-up: #22c55e;
          --color-down: #ef4444;
        }
      `,
    },
  ],
})
