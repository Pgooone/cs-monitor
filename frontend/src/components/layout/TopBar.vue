<template>
  <header class="topbar">
    <div class="topbar-left">
      <h2 class="topbar-title">{{ viewTitle }}</h2>
      <div class="topbar-divider" />
      <div class="topbar-search">
        <Search class="topbar-search__icon" />
        <input
          type="text"
          :placeholder="searchPlaceholder"
          class="topbar-search__input"
        />
      </div>
    </div>
    <div class="topbar-right">
      <button class="topbar-icon-btn" title="刷新数据" @click="handleRefresh">
        <RefreshCw class="w-5 h-5" />
      </button>
      <template v-for="action in contextActions" :key="action.id">
        <button
          :class="action.primary ? 'btn-primary' : 'btn-outline'"
          :style="action.style"
          class="text-xs h-10 px-4"
          @click="action.handler"
        >
          <component :is="action.icon" v-if="action.icon" class="w-4 h-4" />
          {{ action.label }}
        </button>
      </template>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search, RefreshCw, Activity, Upload, Plus, Zap, Download, Save,
} from 'lucide-vue-next'
import { useDashboardStore } from '@/stores/dashboard'
import { useWatchlistStore } from '@/stores/watchlist'
import { toastSuccess } from '@/composables/useToast'

defineProps<{
  collapsed: boolean
  isMobile: boolean
}>()

defineEmits<{
  (e: 'toggle-collapse'): void
  (e: 'toggle-mobile-drawer'): void
}>()

const route = useRoute()
const router = useRouter()
const dashboardStore = useDashboardStore()
const watchlistStore = useWatchlistStore()

const viewTitle = computed(() => {
  const map: Record<string, string> = {
    Dashboard: '数据概览',
    Watchlist: '监控清单',
    ExtremeTrack: '极致追踪',
    Alerts: '历史告警',
    Stats: '市场趋势分析',
    Settings: '系统配置',
    ItemDetail: '饰品详情',
  }
  return map[route.name as string] || '仪表盘'
})

const searchPlaceholder = computed(() => {
  const name = route.name as string
  if (name === 'Alerts') return '在历史告警中搜索 (如: AK-47)...'
  if (name === 'Settings') return '搜索系统配置项...'
  return '快速搜索饰品名称...'
})

interface ContextAction {
  id: string
  label: string
  icon?: typeof Activity
  primary: boolean
  handler: () => void
  style?: string
}

const contextActions = computed<ContextAction[]>(() => {
  const name = route.name as string
  switch (name) {
    case 'Dashboard':
      return [
        { id: 'status', label: '服务状态', icon: Activity, primary: false, handler: () => {} },
        { id: 'sync', label: '强制同步', icon: RefreshCw, primary: true, handler: handleForceSync },
      ]
    case 'Watchlist':
      return [
        { id: 'import', label: '批量导入', icon: Upload, primary: false, handler: () => {} },
        { id: 'add', label: '新增监控项', icon: Plus, primary: true, handler: () => router.push({ name: 'Watchlist', query: { action: 'add' } }) },
      ]
    case 'ExtremeTrack':
      return [
        { id: 'speed', label: 'API 测速', primary: false, handler: () => {}, style: 'color: #22c55e; border-color: rgba(34,197,94,0.3)' },
        { id: 'start', label: '启动新任务', icon: Zap, primary: true, handler: () => {}, style: 'background: #22c55e; color: #000; box-shadow: 0 4px 12px rgba(34,197,94,0.2)' },
      ]
    case 'Alerts':
      return [
        { id: 'export', label: '导出日志', icon: Download, primary: false, handler: () => {} },
      ]
    case 'Settings':
      return [
        { id: 'save', label: '保存全局配置', icon: Save, primary: true, handler: () => {} },
      ]
    default:
      return []
  }
})

function handleRefresh() {
  dashboardStore.loadAll()
  toastSuccess('数据刷新中...')
}

function handleForceSync() {
  watchlistStore.refreshPrices()
  toastSuccess('全量同步已触发')
}
</script>

<style scoped>
.topbar {
  height: 5rem;
  border-bottom: 1px solid #1f1f23;
  background: rgba(5, 5, 5, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  z-index: 40;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.topbar-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #ffffff;
  text-transform: capitalize;
  margin: 0;
}

.topbar-divider {
  height: 1.5rem;
  width: 1px;
  background: #1f1f23;
}

.topbar-search {
  position: relative;
}

.topbar-search__icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: #94a3b8;
  transition: color 200ms;
}

.topbar-search:focus-within .topbar-search__icon {
  color: #6366f1;
}

.topbar-search__input {
  background: #0f0f12;
  border: 1px solid #1f1f23;
  color: #ffffff;
  font-size: 0.75rem;
  border-radius: 0.75rem;
  padding: 0.625rem 1rem 0.625rem 2.75rem;
  width: 12rem;
  transition: all 200ms;
  outline: none;
  font-weight: 500;
}

.topbar-search__input:focus {
  border-color: rgba(99, 102, 241, 0.5);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.05);
  width: 20rem;
}

.topbar-search__input::placeholder {
  color: #71717a;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.topbar-icon-btn {
  padding: 0.625rem;
  color: #94a3b8;
  border-radius: 0.75rem;
  transition: all 200ms;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.topbar-icon-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.05);
}

html:not(.dark) .topbar {
  border-bottom-color: #e2e8f0;
  background: rgba(248, 250, 252, 0.5);
}

html:not(.dark) .topbar-title {
  color: #0f172a;
}

html:not(.dark) .topbar-divider {
  background: #e2e8f0;
}

html:not(.dark) .topbar-search__input {
  background: #ffffff;
  border-color: #e2e8f0;
  color: #0f172a;
}

html:not(.dark) .topbar-search__input:focus {
  border-color: rgba(99, 102, 241, 0.5);
}

html:not(.dark) .topbar-icon-btn {
  color: #64748b;
}

html:not(.dark) .topbar-icon-btn:hover {
  color: #0f172a;
  background: rgba(0, 0, 0, 0.04);
}
</style>
