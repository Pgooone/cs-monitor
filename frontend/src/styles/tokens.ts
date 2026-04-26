/**
 * Design Tokens — CS2 Monitor 设计系统 v2
 *
 * 设计方向：Trading Terminal Pro
 * 参考 BUFF.163.com 等专业饰品交易平台的深色交易界面
 * 深空蓝底 + 电光橙强调 + 高信息密度 + 终端感数字排版
 */

// ===== 品牌色 =====
// 深空蓝系 — 从深邃到明亮，营造专业交易终端氛围
export const brand = {
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

// ===== 电光橙强调色 =====
export const accent = {
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
} as const

// ===== 中性色阶 — 深空蓝调 =====
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
    50: '#080c16',   // 最深底色 — 深空蓝黑
    100: '#0d1320',  // 卡片底色
    200: '#131b2e',  // 悬浮/弹窗底色
    300: '#1a2540',  // 边框/分割
    400: '#243352',  // hover 状态
    500: '#3b5078',  // 禁用/占位
    600: '#5a7ba5',  // 次要文字
    700: '#8da4c8',  // 正文文字
    800: '#b8c9e2',  // 标题文字
    900: '#dce6f2',  // 高亮文字
    950: '#f0f4fa',  // 最亮文字
  },
} as const

// ===== 涨跌颜色（中国 vs 国际） =====
export const riseFall = {
  china: {
    up: '#ef4444',       // 涨 — 红
    down: '#10b981',     // 跌 — 绿
    upBg: 'rgba(239,68,68,0.12)',
    downBg: 'rgba(16,185,129,0.12)',
  },
  international: {
    up: '#10b981',
    down: '#ef4444',
    upBg: 'rgba(16,185,129,0.12)',
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
  glow: '0 0 20px rgba(74, 92, 242, 0.15)',
  glowAccent: '0 0 20px rgba(249, 115, 22, 0.2)',
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
  glow: '0 0 24px rgba(107, 127, 248, 0.15)',
  glowAccent: '0 0 24px rgba(251, 146, 60, 0.2)',
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

// ===== ECharts 颜色序列 — 专业交易配色 =====
export const chartColors = [
  '#6b7ff8',  // 品牌蓝
  '#fb923c',  // 电光橙
  '#34d399',  // 翠绿
  '#f87171',  // 涨红
  '#a78bfa',  // 紫罗兰
  '#38bdf8',  // 天蓝
  '#f472b6',  // 玫瑰
  '#facc15',  // 金黄
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
