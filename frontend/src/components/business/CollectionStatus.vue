<template>
  <div class="collection-status">
    <div class="collection-status__info">
      <div class="collection-status__label">
        <span class="collection-status__dot" :class="{ 'collection-status__dot--idle': !isRunning }" />
        <span>{{ statusText }}</span>
      </div>
      <div class="collection-status__count">
        今日已采集 <strong>{{ todayCollectionCount }}</strong> 次
      </div>
    </div>
    <div v-if="lastUpdate" class="collection-status__progress">
      <div class="collection-status__bar-bg">
        <div
          class="collection-status__bar-fill"
          :style="{ width: `${progressPercent}%`, background: progressColor }"
        />
      </div>
      <div class="collection-status__countdown">
        下次采集: {{ countdownText }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  lastUpdate: string | null
  checkIntervalMinutes: number
  todayCollectionCount: number
}>()

const now = ref(Date.now())
let timer: ReturnType<typeof setInterval> | null = null

const intervalMs = computed(() => props.checkIntervalMinutes * 60 * 1000)

const nextCollectionTime = computed(() => {
  if (!props.lastUpdate) return null
  const last = new Date(props.lastUpdate).getTime()
  if (Number.isNaN(last)) return null
  return last + intervalMs.value
})

const remainingMs = computed(() => {
  const next = nextCollectionTime.value
  if (!next) return 0
  return Math.max(0, next - now.value)
})

const progressPercent = computed(() => {
  if (!nextCollectionTime.value || !props.lastUpdate) return 0
  const total = intervalMs.value
  const remaining = remainingMs.value
  return Math.min(100, Math.max(0, ((total - remaining) / total) * 100))
})

const countdownText = computed(() => {
  const ms = remainingMs.value
  if (ms <= 0) return '即将开始...'
  const m = Math.floor(ms / 60000)
  const s = Math.floor((ms % 60000) / 1000)
  return `${m}分${s.toString().padStart(2, '0')}秒`
})

const isRunning = computed(() => {
  if (!props.lastUpdate) return false
  const last = new Date(props.lastUpdate).getTime()
  return Date.now() - last < intervalMs.value * 2
})

const statusText = computed(() => {
  if (!props.lastUpdate) return '等待首次采集'
  if (isRunning.value) return '监控运行中'
  return '监控可能停滞'
})

const progressColor = computed(() => {
  const p = progressPercent.value
  if (p < 50) return '#10b981'
  if (p < 80) return '#f59e0b'
  return '#ef4444'
})

onMounted(() => {
  timer = setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.collection-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 1rem;
  border-radius: 0.75rem;
  background: var(--n-card-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
}
html.dark .collection-status {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.06);
}
.collection-status__info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-shrink: 0;
}
.collection-status__label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}
.collection-status__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
  animation: pulse-dot 2s infinite;
}
.collection-status__dot--idle {
  background: #a3a3a3;
  box-shadow: none;
  animation: none;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.collection-status__count {
  font-size: 0.8125rem;
  color: var(--n-text-color-2, #525252);
}
.collection-status__count strong {
  font-family: 'JetBrains Mono', monospace;
  color: var(--n-text-color-1, #171717);
}
.collection-status__progress {
  flex: 1;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.collection-status__bar-bg {
  height: 6px;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.06);
  overflow: hidden;
}
html.dark .collection-status__bar-bg {
  background: rgba(255, 255, 255, 0.08);
}
.collection-status__bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s linear;
}
.collection-status__countdown {
  font-size: 0.75rem;
  text-align: right;
  color: var(--n-text-color-3, #737373);
  font-family: 'JetBrains Mono', monospace;
}
</style>
