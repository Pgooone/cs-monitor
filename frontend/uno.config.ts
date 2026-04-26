import { defineConfig, presetUno, presetIcons } from 'unocss'

export default defineConfig({
  presets: [presetUno(), presetIcons()],
  theme: {
    colors: {
      brand: {
        50: '#eef2ff',
        100: '#dce4ff',
        200: '#bfcbff',
        300: '#93a7fd',
        400: '#6b7ff8',
        500: '#4a5cf2',
        600: '#3a3fe6',
        700: '#2f32cc',
        800: '#2a2da5',
        900: '#282c83',
        950: '#1a1b4f',
      },
      accent: {
        50: '#fff7ed',
        100: '#ffedd5',
        200: '#fed7aa',
        300: '#fdba74',
        400: '#fb923c',
        500: '#f97316',
        600: '#ea580c',
        700: '#c2410c',
        800: '#9a3412',
        900: '#7c2d12',
        950: '#431407',
      },
      up: 'var(--color-up, #ef4444)',
      down: 'var(--color-down, #10b981)',
      surface: {
        0: 'var(--cs-bg-page)',
        1: 'var(--cs-bg-card)',
        2: 'var(--cs-bg-elevated)',
      },
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
    },
    boxShadow: {
      xs: '0 1px 2px rgba(0,0,0,0.04)',
      sm: '0 1px 3px rgba(0,0,0,0.06)',
      md: '0 4px 8px rgba(0,0,0,0.08)',
      lg: '0 12px 24px rgba(0,0,0,0.12)',
      glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
      'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.4)',
      glow: '0 0 20px rgba(74, 92, 242, 0.15)',
      'glow-accent': '0 0 20px rgba(249, 115, 22, 0.2)',
    },
  },
  preflights: [
    {
      getCSS: () => `
        html {
          --color-up: #ef4444;
          --color-down: #10b981;
        }
        html.dark {
          --color-up: #ef4444;
          --color-down: #10b981;
        }
        html[data-rise-fall="international"] {
          --color-up: #10b981;
          --color-down: #ef4444;
        }
        html.dark[data-rise-fall="international"] {
          --color-up: #34d399;
          --color-down: #f87171;
        }
      `,
    },
  ],
})
