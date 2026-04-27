<template>
  <div class="alert-feed">
    <div class="alert-feed__list" ref="listRef">
      <transition-group name="alert-item">
        <div
          v-for="item in displayItems"
          :key="item.id"
          class="alert-feed__item"
          :class="{ 'alert-feed__item--new': item._isNew }"
        >
          <div class="alert-feed__dot" :class="`alert-feed__dot--${item.alert_type}`" />
          <div class="alert-feed__content">
            <div class="alert-feed__name">{{ item.display_name || item.market_hash_name }}</div>
            <div class="alert-feed__meta">
              <span :class="changeClass(item.change_percent)">
                {{ formatChange(item.change_percent) }}
              </span>
              <span class="alert-feed__time">{{ formatTime(item.notified_at) }}</span>
            </div>
          </div>
        </div>
      </transition-group>
      <div v-if="displayItems.length === 0" class="alert-feed__empty">
        暂无告警
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref, nextTick } from 'vue'
import { useTheme } from '@/composables/useTheme'
import type { AlertRecord } from '@/api'

interface DisplayAlert extends AlertRecord {
  _isNew?: boolean
}

const props = defineProps<{
  alerts: AlertRecord[]
}>()

const { colorUp, colorDown } = useTheme()
const items = ref<DisplayAlert[]>([])
const listRef = ref<HTMLDivElement>()

// 深拷贝并标记新项
watch(
  () => props.alerts,
  (newAlerts, oldAlerts) => {
    const oldIds = new Set((oldAlerts ?? []).map(a => a.id))
    const merged = newAlerts.map(a => ({
      ...a,
      _isNew: !oldIds.has(a.id),
    }))
    items.value = merged

    // 自动滚动到顶部
    nextTick(() => {
      if (listRef.value) {
        listRef.value.scrollTop = 0
      }
    })

    // 2 秒后移除新项标记
    merged.forEach(a => {
      if (a._isNew) {
        setTimeout(() => {
          const found = items.value.find(i => i.id === a.id)
          if (found) found._isNew = false
        }, 2000)
      }
    })
  },
  { immediate: true, deep: true },
)

const displayItems = computed(() => items.value.slice(0, 20))

function formatChange(v: number | null) {
  if (v == null) return '—'
  const sign = v >= 0 ? '+' : ''
  return `${sign}${v.toFixed(2)}%`
}

function changeClass(v: number | null) {
  if (v == null) return ''
  return v >= 0 ? 'alert-feed__up' : 'alert-feed__down'
}

function formatTime(t: string) {
  try {
    const d = new Date(t)
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return t
  }
}
</script>

<style scoped>
.alert-feed {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 320px;
}
.alert-feed__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding: 0 0.25rem;
}
.alert-feed__title {
  font-size: 1rem;
  font-weight: 600;
}
.alert-feed__list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-right: 0.25rem;
}
.alert-feed__item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.625rem;
  background: var(--n-card-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: background-color 300ms ease;
}
html.dark .alert-feed__item {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.06);
}
.alert-feed__item--new {
  animation: alert-flash 2s ease;
}
@keyframes alert-flash {
  0%, 100% { background-color: transparent; }
  10%, 30% { background-color: rgba(239, 68, 68, 0.12); }
}
html.dark .alert-feed__item--new {
  animation: alert-flash-dark 2s ease;
}
@keyframes alert-flash-dark {
  0%, 100% { background-color: transparent; }
  10%, 30% { background-color: rgba(248, 113, 113, 0.18); }
}
.alert-feed__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-top: 0.5rem;
  flex-shrink: 0;
}
.alert-feed__dot--price_surge { background: #ef4444; }
.alert-feed__dot--price_drop { background: #10b981; }
.alert-feed__dot--both { background: #f59e0b; }
.alert-feed__dot--price_change { background: #3b82f6; }
.alert-feed__dot--quantity_change { background: #8b5cf6; }
.alert-feed__content {
  flex: 1;
  min-width: 0;
}
.alert-feed__name {
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.25rem;
}
.alert-feed__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
}
.alert-feed__up {
  color: v-bind('colorUp');
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
}
.alert-feed__down {
  color: v-bind('colorDown');
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
}
.alert-feed__time {
  color: var(--n-text-color-3, #737373);
  font-size: 0.6875rem;
}
.alert-feed__empty {
  text-align: center;
  padding: 2rem 0;
  color: var(--n-text-color-3, #737373);
  font-size: 0.875rem;
}

/* 列表项进入动画 */
.alert-item-enter-active,
.alert-item-leave-active {
  transition: all 300ms ease;
}
.alert-item-enter-from {
  opacity: 0;
  transform: translateY(-12px);
}
.alert-item-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
