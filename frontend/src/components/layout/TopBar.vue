<template>
  <n-layout-header bordered class="topbar">
    <div class="topbar-left">
      <!-- 移动端菜单按钮 -->
      <n-button
        v-if="isMobile"
        quaternary
        circle
        aria-label="打开菜单"
        @click="$emit('toggle-mobile-drawer')"
      >
        <template #icon>
          <span class="text-lg">☰</span>
        </template>
      </n-button>

      <!-- 折叠/展开按钮（桌面端） -->
      <n-button
        v-else
        quaternary
        circle
        :aria-label="collapsed ? '展开侧边栏' : '折叠侧边栏'"
        @click="$emit('toggle-collapse')"
      >
        <template #icon>
          <span class="text-lg">{{ collapsed ? '→' : '←' }}</span>
        </template>
      </n-button>

      <!-- 全局搜索触发器 -->
      <n-button
        quaternary
        class="topbar-search-trigger"
        aria-label="打开搜索"
        @click="searchModalOpen = true"
      >
        <template #icon>
          <span>🔍</span>
        </template>
        <span class="topbar-search-trigger__text">搜索</span>
        <kbd class="topbar-search-trigger__kbd">{{ modKey }}K</kbd>
      </n-button>
    </div>

    <div class="topbar-right">
      <!-- 主题切换 -->
      <n-tooltip>
        <template #trigger>
          <n-button
            quaternary
            circle
            :aria-label="`当前主题: ${themeLabel}`"
            @click="toggleTheme"
          >
            <template #icon>
              <span class="text-lg">{{ themeIcon }}</span>
            </template>
          </n-button>
        </template>
        {{ themeLabel }}
      </n-tooltip>

      <!-- 告警铃铛 -->
      <n-popover
        trigger="click"
        placement="bottom-end"
        :show-arrow="false"
        style="padding: 0"
      >
        <template #trigger>
          <n-badge :value="unreadCount" :max="99" :show="unreadCount > 0">
            <n-button quaternary circle aria-label="告警通知">
              <template #icon>
                <span class="text-lg">🔔</span>
              </template>
            </n-button>
          </n-badge>
        </template>
        <div class="alert-popover">
          <div class="alert-popover__header">
            <span class="alert-popover__title">实时告警</span>
            <n-button text size="tiny" @click="clearUnread">全部已读</n-button>
          </div>
          <div class="alert-popover__list">
            <div
              v-for="alert in recentAlerts"
              :key="alert.id"
              class="alert-popover__item"
            >
              <div class="alert-popover__item-type">
                {{ alertTypeLabel(alert.alert_type) }}
              </div>
              <div class="alert-popover__item-name">
                {{ alert.market_hash_name }}
              </div>
              <div class="alert-popover__item-meta">
                <span
                  class="alert-popover__item-change"
                  :class="alert.change_percent && alert.change_percent >= 0 ? 'up' : 'down'"
                >
                  {{ formatChange(alert.change_percent) }}
                </span>
                <span class="alert-popover__item-time">{{ formatTime(alert.notified_at) }}</span>
              </div>
            </div>
            <div v-if="recentAlerts.length === 0" class="alert-popover__empty">
              暂无最近告警
            </div>
          </div>
          <div class="alert-popover__footer">
            <n-button text size="small" @click="goToAlerts">
              查看全部告警
            </n-button>
          </div>
        </div>
      </n-popover>

      <!-- 用户菜单 -->
      <n-dropdown
        :options="userMenuOptions"
        placement="bottom-end"
        @select="handleUserMenu"
      >
        <n-button quaternary circle aria-label="用户菜单">
          <template #icon>
            <span class="text-lg">👤</span>
          </template>
        </n-button>
      </n-dropdown>
    </div>

    <!-- 全局搜索模态框 -->
    <n-modal
      v-model:show="searchModalOpen"
      :show-icon="false"
      :mask-closable="true"
      preset="card"
      style="width: 560px; max-width: 90vw"
      class="search-modal"
      @after-leave="searchQuery = ''"
    >
      <n-input
        v-model:value="searchQuery"
        placeholder="搜索页面、饰品..."
        size="large"
        clearable
        autofocus
      >
        <template #prefix>
          <span>🔍</span>
        </template>
      </n-input>
      <div class="search-results">
        <div
          v-for="item in filteredSearchItems"
          :key="item.key"
          class="search-result-item"
          @click="handleSearchClick(item)"
        >
          <span class="search-result-item__icon">{{ item.icon }}</span>
          <div class="search-result-item__info">
            <div class="search-result-item__name">{{ item.name }}</div>
            <div class="search-result-item__desc">{{ item.desc }}</div>
          </div>
        </div>
        <div v-if="filteredSearchItems.length === 0 && searchQuery" class="search-results__empty">
          未找到匹配项
        </div>
      </div>
      <div class="search-footer">
        <kbd class="search-footer__kbd">↑↓</kbd>
        <span>选择</span>
        <kbd class="search-footer__kbd">↵</kbd>
        <span>确认</span>
        <kbd class="search-footer__kbd">Esc</kbd>
        <span>关闭</span>
      </div>
    </n-modal>
  </n-layout-header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  NLayoutHeader,
  NButton,
  NTooltip,
  NPopover,
  NBadge,
  NDropdown,
  NModal,
  NInput,
} from 'naive-ui'
import type { DropdownOption } from 'naive-ui'
import { useTheme } from '@/composables/useTheme'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  collapsed: boolean
  isMobile: boolean
}>()

defineEmits<{
  (e: 'toggle-collapse'): void
  (e: 'toggle-mobile-drawer'): void
}>()

const router = useRouter()
const { themeMode, toggleTheme } = useTheme()
const dashboardStore = useDashboardStore()
const authStore = useAuthStore()

// ===== 主题 =====
const themeIcon = computed(() => {
  switch (themeMode.value) {
    case 'light': return '☀️'
    case 'dark': return '🌙'
    case 'system': return '🖥️'
  }
})

const themeLabel = computed(() => {
  switch (themeMode.value) {
    case 'light': return '浅色模式'
    case 'dark': return '深色模式'
    case 'system': return '跟随系统'
  }
})

// ===== 搜索 =====
const searchModalOpen = ref(false)
const searchQuery = ref('')
const modKey = computed(() => navigator.platform.startsWith('Mac') ? '⌘' : 'Ctrl+')

interface SearchItem {
  key: string
  name: string
  desc: string
  icon: string
  routeName: string
}

const searchItems: SearchItem[] = [
  { key: 'dashboard', name: 'Dashboard', desc: '系统概览与统计', icon: '📊', routeName: 'Dashboard' },
  { key: 'watchlist', name: '监控清单', desc: '管理监控饰品', icon: '📋', routeName: 'Watchlist' },
  { key: 'extreme-track', name: '极致追踪', desc: '高频单品追踪', icon: '🎯', routeName: 'ExtremeTrack' },
  { key: 'alerts', name: '告警记录', desc: '查看历史告警', icon: '🔔', routeName: 'Alerts' },
  { key: 'settings', name: '系统设置', desc: '通知与外观配置', icon: '⚙️', routeName: 'Settings' },
]

const filteredSearchItems = computed(() => {
  if (!searchQuery.value) return searchItems
  const q = searchQuery.value.toLowerCase()
  return searchItems.filter(
    (i) => i.name.toLowerCase().includes(q) || i.desc.toLowerCase().includes(q),
  )
})

function handleSearchClick(item: SearchItem) {
  router.push({ name: item.routeName })
  searchModalOpen.value = false
}

// 键盘快捷键 Cmd/Ctrl+K
function onKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    searchModalOpen.value = true
  }
  if (e.key === 'Escape') {
    searchModalOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})

// ===== 告警铃铛 =====
const unreadCount = ref(0)

const recentAlerts = computed(() => {
  // 优先用 dashboard 的最新告警，限制 20 条
  return (dashboardStore.alerts.slice(0, 20))
})

function alertTypeLabel(type: string) {
  const map: Record<string, string> = {
    price_surge: '📈 价格暴涨',
    price_drop: '📉 价格暴跌',
    both: '🔔 价格+数量变动',
    price_change: '💰 价格变动',
    quantity_change: '📦 数量变动',
  }
  return map[type] || type
}

function formatChange(val: number | null) {
  if (val == null) return '—'
  const sign = val >= 0 ? '+' : ''
  return `${sign}${val.toFixed(2)}%`
}

function formatTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function clearUnread() {
  unreadCount.value = 0
}

function goToAlerts() {
  router.push({ name: 'Alerts' })
}

// ===== 用户菜单 =====
const userMenuOptions: DropdownOption[] = [
  { label: '系统设置', key: 'settings', icon: () => h('span', '⚙️') },
  { type: 'divider', key: 'd1' },
  { label: '退出登录', key: 'logout', icon: () => h('span', '🚪') },
]

function handleUserMenu(key: string) {
  if (key === 'settings') {
    router.push({ name: 'Settings' })
  } else if (key === 'logout') {
    authStore.logout()
    window.location.href = '/login'
  }
}
</script>

<style scoped>
.topbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  position: sticky;
  top: 0;
  z-index: 1020;
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.topbar-search-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  margin-left: 0.5rem;
}

.topbar-search-trigger__text {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
}

.topbar-search-trigger__kbd {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: var(--n-button-color2);
  color: var(--n-text-color-3);
  font-family: 'JetBrains Mono', monospace;
}

/* 告警 popover */
.alert-popover {
  width: 320px;
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.alert-popover__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--n-divider-color);
  font-weight: 600;
}

.alert-popover__list {
  flex: 1;
  overflow-y: auto;
  padding: 0.25rem 0;
}

.alert-popover__item {
  padding: 0.625rem 1rem;
  cursor: pointer;
  transition: background 150ms ease;
}

.alert-popover__item:hover {
  background: var(--n-hover-color);
}

.alert-popover__item-type {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-bottom: 0.125rem;
}

.alert-popover__item-name {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  word-break: break-all;
}

.alert-popover__item-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.alert-popover__item-change.up {
  color: #ef4444;
}

.alert-popover__item-change.down {
  color: #10b981;
}

.alert-popover__item-time {
  color: var(--n-text-color-3);
}

.alert-popover__empty {
  padding: 2rem;
  text-align: center;
  color: var(--n-text-color-3);
  font-size: 0.875rem;
}

.alert-popover__footer {
  padding: 0.5rem 1rem;
  border-top: 1px solid var(--n-divider-color);
  text-align: center;
}

/* 搜索模态框 */
.search-results {
  margin-top: 0.5rem;
  max-height: 320px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 150ms ease;
}

.search-result-item:hover {
  background: var(--n-hover-color);
}

.search-result-item__icon {
  font-size: 1.25rem;
  width: 2rem;
  text-align: center;
  flex-shrink: 0;
}

.search-result-item__name {
  font-size: 0.875rem;
  font-weight: 500;
}

.search-result-item__desc {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

.search-results__empty {
  padding: 2rem;
  text-align: center;
  color: var(--n-text-color-3);
  font-size: 0.875rem;
}

.search-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--n-divider-color);
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

.search-footer__kbd {
  font-family: 'JetBrains Mono', monospace;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: var(--n-button-color2);
  font-size: 0.75rem;
}
</style>
