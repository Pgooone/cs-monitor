/**
 * Naive UI Theme Overrides — Trading Terminal Pro
 *
 * 将 Design Tokens 映射到 Naive UI 的 themeOverrides 结构。
 * light / dark 两套配置，与 useTheme 联动。
 */

import type { GlobalThemeOverrides } from 'naive-ui'
import { brand, semantic, neutral, fontFamily } from './tokens'

const lightCommon: GlobalThemeOverrides['common'] = {
  primaryColor: brand[500],
  primaryColorHover: brand[400],
  primaryColorPressed: brand[600],
  primaryColorSuppl: brand[500],

  infoColor: semantic.info.light,
  infoColorHover: '#60a5fa',
  infoColorPressed: '#2563eb',
  infoColorSuppl: semantic.info.light,

  successColor: semantic.success.light,
  successColorHover: '#34d399',
  successColorPressed: '#059669',
  successColorSuppl: semantic.success.light,

  warningColor: semantic.warning.light,
  warningColorHover: '#fbbf24',
  warningColorPressed: '#d97706',
  warningColorSuppl: semantic.warning.light,

  errorColor: semantic.error.light,
  errorColorHover: '#f87171',
  errorColorPressed: '#dc2626',
  errorColorSuppl: semantic.error.light,

  textColorBase: neutral.light[900],
  textColor1: neutral.light[900],
  textColor2: neutral.light[600],
  textColor3: neutral.light[400],

  bodyColor: '#f0f2f7',
  cardColor: '#ffffff',
  modalColor: '#ffffff',
  popoverColor: '#ffffff',
  dividerColor: neutral.light[200],
  borderColor: neutral.light[200],
  tableHeaderColor: '#f8f9fc',

  hoverColor: neutral.light[100],
  pressedColor: neutral.light[200],

  fontFamily: fontFamily.sans,
  fontFamilyMono: fontFamily.mono,

  borderRadius: '8px',
  borderRadiusSmall: '6px',

  heightSmall: '28px',
  heightMedium: '34px',
  heightLarge: '40px',

  fontSizeSmall: '13px',
  fontSizeMedium: '14px',
  fontSizeLarge: '14px',

  boxShadow1: '0 1px 2px rgba(0,0,0,0.04)',
  boxShadow2: '0 4px 12px rgba(0,0,0,0.08)',
  boxShadow3: '0 12px 24px rgba(0,0,0,0.12)',
}

const darkCommon: GlobalThemeOverrides['common'] = {
  primaryColor: '#6b7ff8',
  primaryColorHover: '#7e91fa',
  primaryColorPressed: '#4a5cf2',
  primaryColorSuppl: '#6b7ff8',

  infoColor: '#60a5fa',
  infoColorHover: '#93c5fd',
  infoColorPressed: '#3b82f6',
  infoColorSuppl: '#60a5fa',

  successColor: '#34d399',
  successColorHover: '#6ee7b7',
  successColorPressed: '#10b981',
  successColorSuppl: '#34d399',

  warningColor: '#fbbf24',
  warningColorHover: '#fcd34d',
  warningColorPressed: '#f59e0b',
  warningColorSuppl: '#fbbf24',

  errorColor: '#f87171',
  errorColorHover: '#fca5a5',
  errorColorPressed: '#ef4444',
  errorColorSuppl: '#f87171',

  textColorBase: '#dce6f2',
  textColor1: '#dce6f2',
  textColor2: '#8da4c8',
  textColor3: '#5a7ba5',

  bodyColor: '#080c16',
  cardColor: '#0d1320',
  modalColor: '#131b2e',
  popoverColor: '#131b2e',
  dividerColor: 'rgba(255,255,255,0.06)',
  borderColor: 'rgba(255,255,255,0.08)',
  tableHeaderColor: '#0d1320',

  hoverColor: 'rgba(255,255,255,0.04)',
  pressedColor: 'rgba(255,255,255,0.06)',

  fontFamily: fontFamily.sans,
  fontFamilyMono: fontFamily.mono,

  borderRadius: '8px',
  borderRadiusSmall: '6px',

  heightSmall: '28px',
  heightMedium: '34px',
  heightLarge: '40px',

  fontSizeSmall: '13px',
  fontSizeMedium: '14px',
  fontSizeLarge: '14px',

  boxShadow1: '0 1px 3px rgba(0,0,0,0.3)',
  boxShadow2: '0 4px 12px rgba(0,0,0,0.35)',
  boxShadow3: '0 12px 24px rgba(0,0,0,0.45)',
}

export const lightThemeOverrides: GlobalThemeOverrides = {
  common: lightCommon,
  Button: {
    fontWeight: '500',
  },
  Card: {
    borderRadius: '12px',
    borderColor: '#e2e6ef',
  },
  DataTable: {
    borderRadius: '12px',
    thFontSize: '12px',
    tdFontSize: '13px',
  },
  Input: {
    borderRadius: '8px',
  },
  Tag: {
    borderRadius: '6px',
  },
}

export const darkThemeOverrides: GlobalThemeOverrides = {
  common: darkCommon,
  Button: {
    fontWeight: '500',
  },
  Card: {
    borderRadius: '12px',
    borderColor: 'rgba(255,255,255,0.06)',
    color: '#0d1320',
  },
  DataTable: {
    borderRadius: '12px',
    thFontSize: '12px',
    tdFontSize: '13px',
    thColor: '#0d1320',
    tdColor: 'transparent',
    borderColor: 'rgba(255,255,255,0.04)',
  },
  Input: {
    borderRadius: '8px',
    color: 'rgba(255,255,255,0.04)',
    borderColor: 'rgba(255,255,255,0.08)',
    colorFocus: 'rgba(255,255,255,0.06)',
  },
  Tag: {
    borderRadius: '6px',
  },
  Modal: {
    borderRadius: '16px',
  },
}
