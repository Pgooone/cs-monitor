<template>
  <div class="sidebar-inner" :class="{ 'sidebar-inner--collapsed': collapsed }">
    <!-- 顶部品牌色渐变线 -->
    <div class="sidebar-accent-line" />

    <!-- Logo 区 -->
    <div class="sidebar-logo">
      <div class="sidebar-logo__icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#6b7ff8" />
              <stop offset="100%" stop-color="#fb923c" />
            </linearGradient>
          </defs>
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <span v-if="!collapsed" class="sidebar-logo__wordmark">CS2 Monitor</span>
    </div>

    <!-- 导航菜单 -->
    <n-menu
      :collapsed="collapsed"
      :collapsed-width="64"
      :collapsed-icon-size="22"
      :options="menuOptions"
      :value="activeKey"
      class="sidebar-menu"
    />

    <!-- 底部信息 -->
    <div class="sidebar-footer">
      <div v-if="!collapsed" class="sidebar-footer__row">
        <span class="sidebar-footer__version">v1.0.0</span>
        <n-button text tag="a" href="https://github.com" target="_blank" aria-label="GitHub">
          <template #icon>
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
          </template>
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute } from 'vue-router'
import { NMenu, NButton } from 'naive-ui'
import type { MenuOption, MenuGroupOption } from 'naive-ui'
import { RouterLink } from 'vue-router'

defineProps<{
  collapsed: boolean
  showTooltip: boolean
}>()

defineEmits<{
  (e: 'navigate'): void
}>()

const route = useRoute()

const activeKey = computed(() => route.name as string)

function renderIcon(icon: string) {
  return () => h('span', { class: 'text-base' }, icon)
}

function renderLabel(name: string, label: string) {
  return () => h(RouterLink, { to: { name } }, { default: () => label })
}

const menuOptions: (MenuOption | MenuGroupOption)[] = [
  {
    type: 'group',
    label: '监控',
    key: 'group-monitor',
    children: [
      {
        label: renderLabel('Dashboard', 'Dashboard'),
        key: 'Dashboard',
        icon: renderIcon('📊'),
      },
      {
        label: renderLabel('Watchlist', '监控清单'),
        key: 'Watchlist',
        icon: renderIcon('📋'),
      },
      {
        label: renderLabel('ExtremeTrack', '极致追踪'),
        key: 'ExtremeTrack',
        icon: renderIcon('🎯'),
      },
    ],
  },
  {
    type: 'group',
    label: '告警',
    key: 'group-alerts',
    children: [
      {
        label: renderLabel('Alerts', '告警记录'),
        key: 'Alerts',
        icon: renderIcon('🔔'),
      },
    ],
  },
  {
    type: 'group',
    label: '系统',
    key: 'group-system',
    children: [
      {
        label: renderLabel('Settings', '系统设置'),
        key: 'Settings',
        icon: renderIcon('⚙️'),
      },
    ],
  },
]
</script>

<style scoped>
.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 顶部品牌渐变线 — 电光橙到品牌蓝 */
.sidebar-accent-line {
  height: 2px;
  flex-shrink: 0;
  background: linear-gradient(90deg, #6b7ff8 0%, #fb923c 50%, #6b7ff8 100%);
  opacity: 0.8;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  height: 56px;
  padding: 0 1rem;
  flex-shrink: 0;
  border-bottom: 1px solid transparent;
  transition: border-color 200ms ease;
}

.sidebar-logo__icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  transition: transform 200ms ease;
}

.sidebar-logo__icon:hover {
  transform: scale(1.1);
}

.sidebar-logo__icon svg {
  width: 100%;
  height: 100%;
}

.sidebar-logo__wordmark {
  font-size: 0.9375rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #6b7ff8, #fb923c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  padding-top: 0.5rem;
}

.sidebar-footer {
  flex-shrink: 0;
  padding: 0.625rem 1rem;
  border-top: 1px solid transparent;
  transition: border-color 200ms ease;
}

.sidebar-footer__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.375rem;
}

.sidebar-footer__version {
  font-size: 0.6875rem;
  font-family: 'JetBrains Mono', monospace;
  color: var(--n-text-color-3);
  opacity: 0.7;
}


/* 折叠状态微调 */
.sidebar-inner--collapsed .sidebar-logo {
  justify-content: center;
  padding: 0;
}

/* 深色模式边框色 */
html.dark .sidebar-logo,
html.dark .sidebar-footer {
  border-color: rgba(255, 255, 255, 0.04);
}

html:not(.dark) .sidebar-logo,
html:not(.dark) .sidebar-footer {
  border-color: rgba(0, 0, 0, 0.06);
}
</style>
