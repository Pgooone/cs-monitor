/**
 * Design Tokens — CS2 Monitor 设计系统 v3
 *
 * 设计方向：极客黑（Geek Black）
 * 参考 React 版视觉效果：近纯黑底 + Indigo 品牌色 + 玻璃拟态
 */

// ===== 品牌色 =====
// Indigo 紫蓝系 — 现代极客风格
export const brand = {
  50: '#eef2ff',
  100: '#e0e7ff',
  200: '#c7d2fe',
  300: '#a5b4fc',
  400: '#818cf8',   // 深色模式主色
  500: '#6366f1',   // 浅色模式主色 (Indigo-500)
  600: '#4f46e5',
  700: '#4338ca',
  800: '#3730a3',
  900: '#312e81',
  950: '#1e1b4b',
} as const

// ===== 功能色 =====
export const semantic = {
  success: {
    light: '#10b981',
    dark: '#34d399',
  },
  warning: {
    light: '#f59e0b',
    dark: '#fbbf24',
  },
  error: {
    light: '#ef4444',
    dark: '#f87171',
  },
  info: {
    light: '#3b82f6',
    dark: '#60a5fa',
  },
} as const

// ===== 中性色阶 — 极客黑调 =====
export const neutral = {
  light: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    950: '#020617',
  },
  dark: {
    50: '#050505',    // 页面背景（近纯黑）
    100: '#0f0f12',   // 卡片背景
    200: '#16161d',   // 悬停表面
    300: '#1f1f23',   // 边框
    400: '#2d2d35',   // 高亮边框
    500: '#3f3f46',   // 禁用/占位
    600: '#71717a',   // 次要文字
    700: '#94a3b8',   // 正文次要文字 (on-muted)
    800: '#cbd5e1',   // 标题文字
    900: '#ffffff',   // 主文字 (on-bg)
    950: '#ffffff',
  },
} as const

// ===== 涨跌颜色（中国 vs 国际） =====
export const riseFall = {
  china: {
    up: '#ef4444',       // 涨 — 红
    down: '#22c55e',     // 跌 — 绿
    upBg: 'rgba(239,68,68,0.12)',
    downBg: 'rgba(34,197,94,0.12)',
  },
  international: {
    up: '#22c55e',
    down: '#ef4444',
    upBg: 'rgba(34,197,94,0.12)',
    downBg: 'rgba(239,68,68,0.12)',
  },
} as const

export type RiseFallMode = 'china' | 'international'

// ===== 字体 =====
export const fontFamily = {
  sans: "'Inter', 'PingFang SC', 'Microsoft YaHei', 'HarmonyOS Sans', sans-serif",
  mono: "'JetBrains Mono', 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
  display: "'Inter', 'PingFang SC', sans-serif",
} as const

// ===== 字号 =====
export const fontSize = {
  '2xs': '0.6875rem',  // 11px — 极小标签
  xs: '0.75rem',       // 12px — 辅助文字
  sm: '0.8125rem',     // 13px — 正文（比标准略小，提升信息密度）
  base: '0.875rem',    // 14px — 标准正文
  lg: '1rem',          // 16px — 小标题
  xl: '1.125rem',      // 18px — 标题
  '2xl': '1.375rem',   // 22px — 大标题
  '3xl': '1.75rem',    // 28px — 页面标题
  '4xl': '2.25rem',    // 36px — hero 数字
} as const

// ===== 间距 =====
export const spacing = {
  0: '0',
  0.5: '0.125rem',
  1: '0.25rem',
  1.5: '0.375rem',
  2: '0.5rem',
  2.5: '0.625rem',
  3: '0.75rem',
  3.5: '0.875rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
  24: '6rem',
} as const

// ===== 圆角 =====
export const radius = {
  none: '0',
  xs: '0.1875rem',   // 3px
  sm: '0.375rem',    // 6px
  base: '0.5rem',    // 8px
  md: '0.625rem',    // 10px
  lg: '0.75rem',     // 12px — 卡片默认
  xl: '1rem',        // 16px — 大卡片
  '2xl': '1.25rem',  // 20px — 弹窗
  '3xl': '1.5rem',   // 24px
  full: '9999px',
} as const

// ===== 阴影 =====
export const shadow = {
  xs: '0 1px 2px 0 rgb(0 0 0 / 0.03)',
  sm: '0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
  base: '0 2px 4px -1px rgb(0 0 0 / 0.08), 0 1px 2px -2px rgb(0 0 0 / 0.06)',
  md: '0 4px 8px -2px rgb(0 0 0 / 0.1), 0 2px 4px -3px rgb(0 0 0 / 0.08)',
  lg: '0 12px 24px -4px rgb(0 0 0 / 0.12), 0 4px 8px -4px rgb(0 0 0 / 0.08)',
  xl: '0 24px 48px -8px rgb(0 0 0 / 0.16), 0 8px 16px -6px rgb(0 0 0 / 0.1)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.06)',
  glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
  glow: '0 0 15px rgba(99, 102, 241, 0.4)',
  glowAccent: '0 0 15px rgba(99, 102, 241, 0.2)',
} as const

export const shadowDark = {
  xs: '0 1px 2px 0 rgb(0 0 0 / 0.2)',
  sm: '0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.3)',
  base: '0 2px 4px -1px rgb(0 0 0 / 0.35), 0 1px 2px -2px rgb(0 0 0 / 0.3)',
  md: '0 4px 8px -2px rgb(0 0 0 / 0.4), 0 2px 4px -3px rgb(0 0 0 / 0.35)',
  lg: '0 12px 24px -4px rgb(0 0 0 / 0.45), 0 4px 8px -4px rgb(0 0 0 / 0.35)',
  xl: '0 24px 48px -8px rgb(0 0 0 / 0.5), 0 8px 16px -6px rgb(0 0 0 / 0.4)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.3)',
  glass: '0 8px 32px 0 rgba(0, 0, 0, 0.4)',
  glow: '0 0 15px rgba(99, 102, 241, 0.4)',
  glowAccent: '0 0 15px rgba(99, 102, 241, 0.2)',
} as const

// ===== 动效 =====
export const transition = {
  fast: '100ms cubic-bezier(0.25, 1, 0.5, 1)',
  base: '200ms cubic-bezier(0.25, 1, 0.5, 1)',
  slow: '300ms cubic-bezier(0.25, 1, 0.5, 1)',
  page: '240ms cubic-bezier(0.25, 1, 0.5, 1)',
  color: '150ms ease',
  spring: '400ms cubic-bezier(0.34, 1.56, 0.64, 1)',
} as const

// ===== ECharts 颜色序列 =====
export const chartColors = [
  '#6366f1',  // 品牌紫
  '#06b6d4',  // 青色
  '#22c55e',  // 绿色
  '#ef4444',  // 红色
  '#a855f7',  // 紫色
  '#3b82f6',  // 蓝色
  '#ec4899',  // 粉色
  '#eab308',  // 黄色
] as const

// ===== Z-Index =====
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
} as const
