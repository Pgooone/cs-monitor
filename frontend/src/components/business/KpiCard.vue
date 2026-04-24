<template>
  <div
    class="kpi-card"
    :class="[`kpi-card--${variant}`, { 'kpi-card--glass': glass }]"
  >
    <div class="kpi-card__header">
      <div
        class="kpi-card__icon"
        :style="{ background: iconBg, color: iconColor }"
      >
        <slot name="icon">
          <span>{{ icon }}</span>
        </slot>
      </div>
      <span class="kpi-card__title">{{ title }}</span>
    </div>
    <div class="kpi-card__body">
      <slot>
        <div class="kpi-card__value" :style="{ color: valueColor }">
          {{ formattedValue }}
        </div>
      </slot>
    </div>
    <div v-if="$slots.extra" class="kpi-card__extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  title: string
  value?: string | number
  icon?: string
  iconColor?: string
  iconBg?: string
  valueColor?: string
  variant?: 'default' | 'brand' | 'success' | 'warning' | 'error'
  glass?: boolean
}>(), {
  value: '',
  icon: '📊',
  iconColor: '#3b82f6',
  iconBg: 'rgba(59, 130, 246, 0.12)',
  valueColor: 'inherit',
  variant: 'default',
  glass: false,
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString('zh-CN')
  }
  return props.value
})
</script>

<style scoped>
.kpi-card {
  position: relative;
  border-radius: 1rem;
  padding: 1.25rem;
  transition: transform 200ms ease, box-shadow 200ms ease;
  border: 1px solid transparent;
  overflow: hidden;
}
.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-card--default {
  background: var(--n-card-color, #fff);
  border-color: rgba(0, 0, 0, 0.06);
}
html.dark .kpi-card--default {
  border-color: rgba(255, 255, 255, 0.06);
}

.kpi-card--brand {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
}
.kpi-card--success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}
.kpi-card--warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
}
.kpi-card--error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
}

.kpi-card--glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border-color: rgba(255, 255, 255, 0.3);
}
html.dark .kpi-card--glass {
  background: rgba(23, 23, 23, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
}

.kpi-card__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.kpi-card__icon {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}
.kpi-card__title {
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0.85;
}
.kpi-card__body {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
}
.kpi-card__value {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
.kpi-card__extra {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}
.kpi-card--brand .kpi-card__extra,
.kpi-card--success .kpi-card__extra,
.kpi-card--warning .kpi-card__extra,
.kpi-card--error .kpi-card__extra {
  border-top-color: rgba(255, 255, 255, 0.2);
}
html.dark .kpi-card__extra {
  border-top-color: rgba(255, 255, 255, 0.08);
}
</style>
