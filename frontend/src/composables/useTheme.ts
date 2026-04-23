/**
 * useTheme — 全局主题管理 Composable
 *
 * 管理 light/dark/system 三种主题模式、涨跌颜色偏好，
 * 自动同步到 localStorage 和 html class。
 */

import { ref, computed, watch, onMounted } from 'vue'
import { type RiseFallMode, riseFall, brand, semantic, neutral, fontFamily, radius, shadow, shadowDark, spacing, transition } from '@/styles/tokens'

export type ThemeMode = 'light' | 'dark' | 'system'

const THEME_KEY = 'cs_monitor_theme_mode'
const RISE_FALL_KEY = 'cs_monitor_rise_fall_mode'

const themeMode = ref<ThemeMode>('system')
const riseFallMode = ref<RiseFallMode>('china')
const systemIsDark = ref(false)

export function useTheme() {
  onMounted(() => {
    // 从 localStorage 恢复
    const savedTheme = localStorage.getItem(THEME_KEY) as ThemeMode | null
    const savedRiseFall = localStorage.getItem(RISE_FALL_KEY) as RiseFallMode | null

    if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
      themeMode.value = savedTheme
    }
    if (savedRiseFall && ['china', 'international'].includes(savedRiseFall)) {
      riseFallMode.value = savedRiseFall
    }

    // 监听系统 prefers-color-scheme
    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    systemIsDark.value = mql.matches
    const handler = (e: MediaQueryListEvent) => {
      systemIsDark.value = e.matches
    }
    mql.addEventListener('change', handler)

    // 清理函数由调用方负责（组件卸载时）
    return () => {
      mql.removeEventListener('change', handler)
    }
  })

  const isDark = computed(() => {
    if (themeMode.value === 'system') {
      return systemIsDark.value
    }
    return themeMode.value === 'dark'
  })

  // 同步 html class
  watch(
    isDark,
    (dark) => {
      const html = document.documentElement
      if (dark) {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
    },
    { immediate: true },
  )

  // 同步涨跌颜色到 html data 属性（供 UnoCSS preflights 使用）
  watch(
    riseFallMode,
    (mode) => {
      document.documentElement.setAttribute('data-rise-fall', mode)
    },
    { immediate: true },
  )

  // 持久化
  watch(themeMode, (v) => {
    localStorage.setItem(THEME_KEY, v)
  })

  watch(riseFallMode, (v) => {
    localStorage.setItem(RISE_FALL_KEY, v)
  })

  const colorUp = computed(() => riseFall[riseFallMode.value].up)
  const colorDown = computed(() => riseFall[riseFallMode.value].down)

  function setTheme(mode: ThemeMode) {
    themeMode.value = mode
  }

  function setRiseFall(mode: RiseFallMode) {
    riseFallMode.value = mode
  }

  function toggleTheme() {
    const order: ThemeMode[] = ['light', 'dark', 'system']
    const idx = order.indexOf(themeMode.value)
    themeMode.value = order[(idx + 1) % order.length]
  }

  return {
    themeMode,
    riseFallMode,
    isDark,
    colorUp,
    colorDown,
    setTheme,
    setRiseFall,
    toggleTheme,
  }
}

/** 纯静态 tokens，不响应主题变化（供无需响应式的场景使用） */
export const tokens = {
  brand,
  semantic,
  neutral,
  fontFamily,
  radius,
  spacing,
  transition,
  shadow,
  shadowDark,
}
