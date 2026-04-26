<template>
  <div class="kpi-card" :class="cardClasses">
    <div class="kpi-card__header">
      <div class="kpi-card__icon" :style="{ background: iconBg, color: iconColor }">
        <slot name="icon">
          <span>{{ icon }}</span>
        </slot>
      </div>
      <span class="kpi-card__title">{{ title }}</span>
    </div>
    <div class="kpi-card__body">
      <slot>
        <div class="kpi-card__value" :style="valueStyle">{{ formattedValue }}</div>
      </slot>
    </div>
    <div v-if="$slots.extra" class="kpi-card__extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value?: string | number
  icon?: string
  iconColor?: string
  iconBg?: string
  valueColor?: string
  variant?: 'default' | 'brand' | 'success' | 'warning' | 'error' | 'accent'
  glass?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  value: '',
  icon: '📊',
  iconColor: '#6b7ff8',
  iconBg: 'rgba(107, 127, 248, 0.1)',
  valueColor: 'inherit',
  variant: 'default',
  glass: false,
})

const cardClasses = computed(() => {
  const classes: string[] = [`kpi-card--${props.variant}`]
  if (props.glass) classes.push('kpi-card--glass')
  return classes
})

const valueStyle = computed(() => {
  if (props.valueColor && props.valueColor !== 'inherit') {
    return { color: props.valueColor }
  }
  return {}
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
  border-radius: 12px;
  padding: 1rem 1.125rem;
  transition: transform 200ms cubic-bezier(0.25, 1, 0.5, 1), box-shadow 200ms cubic-bezier(0.25, 1, 0.5, 1);
  border: 1px solid transparent;
  overflow: hidden;
}
.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-card--default {
  background: var(--cs-bg-card);
  border-color: var(--cs-border-light);
  box-shadow: var(--cs-shadow-xs);
}
.kpi-card--default:hover {
  box-shadow: var(--cs-shadow-sm);
  border-color: rgba(107, 127, 248, 0.12);
}

.kpi-card--brand {
  background: linear-gradient(135deg, #4a5cf2 0%, #2f32cc 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(74, 92, 242, 0.2);
}
.kpi-card--brand:hover {
  box-shadow: 0 6px 24px rgba(74, 92, 242, 0.3);
}

.kpi-card--success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
}
.kpi-card--success:hover {
  box-shadow: 0 6px 24px rgba(16, 185, 129, 0.3);
}

.kpi-card--warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.2);
}
.kpi-card--warning:hover {
  box-shadow: 0 6px 24px rgba(245, 158, 11, 0.3);
}

.kpi-card--error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2);
}
.kpi-card--error:hover {
  box-shadow: 0 6px 24px rgba(239, 68, 68, 0.3);
}

.kpi-card--accent {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(249, 115, 22, 0.2);
}
.kpi-card--accent:hover {
  box-shadow: 0 6px 24px rgba(249, 115, 22, 0.3);
}

.kpi-card--glass {
  background: var(--cs-bg-glass);
  backdrop-filter: blur(16px) saturate(1.2);
  -webkit-backdrop-filter: blur(16px) saturate(1.2);
  border-color: var(--cs-border-light);
  box-shadow: var(--cs-shadow-sm);
}
.kpi-card--glass:hover {
  box-shadow: var(--cs-shadow-md);
}

.kpi-card__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.625rem;
}
.kpi-card__icon {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  flex-shrink: 0;
}
.kpi-card__title {
  font-size: 0.8125rem;
  font-weight: 500;
  opacity: 0.8;
  letter-spacing: 0.01em;
}
.kpi-card__body {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
}
.kpi-card__value {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}
.kpi-card__extra {
  margin-top: 0.625rem;
  padding-top: 0.625rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}
.kpi-card--brand .kpi-card__extra,
.kpi-card--success .kpi-card__extra,
.kpi-card--warning .kpi-card__extra,
.kpi-card--error .kpi-card__extra,
.kpi-card--accent .kpi-card__extra {
  border-top-color: rgba(255, 255, 255, 0.15);
}
html.dark .kpi-card__extra {
  border-top-color: rgba(255, 255, 255, 0.06);
}
</style>
