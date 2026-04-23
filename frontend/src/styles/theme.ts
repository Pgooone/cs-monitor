/**
 * Naive UI Theme Overrides
 *
 * 将 Design Tokens 映射到 Naive UI 的 themeOverrides 结构。
 * light / dark 两套配置，与 useTheme 联动。
 */

import type { GlobalThemeOverrides } from 'naive-ui'
import { brand, semantic, neutral, fontFamily, radius } from './tokens'

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
  textColor2: neutral.light[700],
  textColor3: neutral.light[500],

  bodyColor: neutral.light[50],
  cardColor: '#ffffff',
  modalColor: '#ffffff',
  popoverColor: '#ffffff',
  dividerColor: neutral.light[200],
  borderColor: neutral.light[200],
  tableHeaderColor: neutral.light[100],

  hoverColor: neutral.light[100],
  pressedColor: neutral.light[200],

  fontFamily: fontFamily.sans,
  fontFamilyMono: fontFamily.mono,

  borderRadius: radius.md,
  borderRadiusSmall: radius.sm,
}

const darkCommon: GlobalThemeOverrides['common'] = {
  primaryColor: brand[400],
  primaryColorHover: brand[300],
  primaryColorPressed: brand[500],
  primaryColorSuppl: brand[400],

  infoColor: semantic.info.dark,
  infoColorHover: '#93c5fd',
  infoColorPressed: '#3b82f6',
  infoColorSuppl: semantic.info.dark,

  successColor: semantic.success.dark,
  successColorHover: '#6ee7b7',
  successColorPressed: '#10b981',
  successColorSuppl: semantic.success.dark,

  warningColor: semantic.warning.dark,
  warningColorHover: '#fcd34d',
  warningColorPressed: '#f59e0b',
  warningColorSuppl: semantic.warning.dark,

  errorColor: semantic.error.dark,
  errorColorHover: '#fca5a5',
  errorColorPressed: '#ef4444',
  errorColorSuppl: semantic.error.dark,

  textColorBase: neutral.dark[900],
  textColor1: neutral.dark[900],
  textColor2: neutral.dark[700],
  textColor3: neutral.dark[500],

  bodyColor: neutral.dark[50],
  cardColor: neutral.dark[100],
  modalColor: neutral.dark[100],
  popoverColor: neutral.dark[100],
  dividerColor: neutral.dark[200],
  borderColor: neutral.dark[200],
  tableHeaderColor: neutral.dark[100],

  hoverColor: neutral.dark[200],
  pressedColor: neutral.dark[300],

  fontFamily: fontFamily.sans,
  fontFamilyMono: fontFamily.mono,

  borderRadius: radius.md,
  borderRadiusSmall: radius.sm,
}

export const lightThemeOverrides: GlobalThemeOverrides = {
  common: lightCommon,
}

export const darkThemeOverrides: GlobalThemeOverrides = {
  common: darkCommon,
}
