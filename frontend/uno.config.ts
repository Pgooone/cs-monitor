import { defineConfig, presetUno, presetIcons } from 'unocss'

export default defineConfig({
  presets: [presetUno(), presetIcons()],
  theme: {
    colors: {
      brand: {
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
        950: '#172554',
      },
      up: 'var(--color-up, #ef4444)',
      down: 'var(--color-down, #10b981)',
    },
    fontFamily: {
      sans: "'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif",
      mono: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
    },
    borderRadius: {
      sm: '0.25rem',
      base: '0.375rem',
      md: '0.5rem',
      lg: '0.75rem',
      xl: '1rem',
      '2xl': '1.5rem',
    },
    boxShadow: {
      glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
      'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.35)',
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
