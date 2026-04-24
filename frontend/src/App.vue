<template>
  <n-config-provider
    :theme="naiveTheme"
    :theme-overrides="themeOverrides"
  >
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <router-view />
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  darkTheme,
  NConfigProvider,
  NMessageProvider,
  NDialogProvider,
  NNotificationProvider,
} from 'naive-ui'
import { useTheme } from '@/composables/useTheme'
import { lightThemeOverrides, darkThemeOverrides } from '@/styles/theme'
import { registerCsMonitorThemes } from '@/charts/theme'

// 注册 ECharts 自定义主题
registerCsMonitorThemes()

const { isDark } = useTheme()

const naiveTheme = computed(() => (isDark.value ? darkTheme : null))
const themeOverrides = computed(() =>
  isDark.value ? darkThemeOverrides : lightThemeOverrides,
)
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 等宽数字字体 */
.font-mono-num {
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-variant-numeric: tabular-nums;
}
</style>
