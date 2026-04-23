<template>
  <div
    v-if="showPill"
    class="ws-status-pill"
    :class="`ws-status-pill--${overallStatus}`"
    role="status"
    :aria-label="ariaLabel"
  >
    <span class="ws-status-pill__dot" />
    <span class="ws-status-pill__text">{{ statusText }}</span>
    <span v-if="activeCount > 0" class="ws-status-pill__count">{{ activeCount }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWebsocketStore } from '@/stores/websocket'

const wsStore = useWebsocketStore()

const overallStatus = computed(() => wsStore.overallStatus)
const activeCount = computed(() => wsStore.activeConnectionCount)

const showPill = computed(() => overallStatus.value !== 'idle')

const statusText = computed(() => {
  switch (overallStatus.value) {
    case 'connecting':
      return '连接中...'
    case 'connected':
      return '实时推送'
    case 'disconnected':
      return '已断开'
    case 'error':
      return '连接异常'
    default:
      return ''
  }
})

const ariaLabel = computed(() => {
  const base = statusText.value
  if (activeCount.value > 0) {
    return `${base}，${activeCount.value} 个活跃连接`
  }
  return base
})
</script>

<style scoped>
.ws-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  backdrop-filter: blur(8px);
  transition: all 200ms ease;
  user-select: none;
}

.ws-status-pill--connecting {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.25);
}
html.dark .ws-status-pill--connecting {
  background: rgba(251, 191, 36, 0.12);
  color: #fbbf24;
  border-color: rgba(251, 191, 36, 0.25);
}

.ws-status-pill--connected {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.25);
}
html.dark .ws-status-pill--connected {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
  border-color: rgba(52, 211, 153, 0.25);
}

.ws-status-pill--disconnected {
  background: rgba(107, 114, 128, 0.12);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.25);
}
html.dark .ws-status-pill--disconnected {
  background: rgba(156, 163, 175, 0.12);
  color: #9ca3af;
  border-color: rgba(156, 163, 175, 0.25);
}

.ws-status-pill--error {
  background: rgba(239, 68, 68, 0.12);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.25);
}
html.dark .ws-status-pill--error {
  background: rgba(248, 113, 113, 0.12);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.25);
}

.ws-status-pill__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.ws-status-pill--connecting .ws-status-pill__dot {
  animation: ws-pulse 1.5s infinite;
}

.ws-status-pill--connected .ws-status-pill__dot {
  background: currentColor;
}

.ws-status-pill__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1rem;
  height: 1rem;
  padding: 0 0.25rem;
  border-radius: 9999px;
  background: currentColor;
  color: #fff;
  font-size: 0.625rem;
  font-weight: 600;
}

@keyframes ws-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
