import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'

const messages = {
  'zh-CN': zhCN,
  'en-US': enUS,
}

const savedLocale = localStorage.getItem('cs_monitor_locale') as keyof typeof messages | null
const defaultLocale: keyof typeof messages = savedLocale || 'zh-CN'

export const i18n = createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: 'zh-CN',
  messages,
})

export function setLocale(locale: keyof typeof messages) {
  i18n.global.locale.value = locale
  localStorage.setItem('cs_monitor_locale', locale)
}

export type LocaleKey = keyof typeof messages
