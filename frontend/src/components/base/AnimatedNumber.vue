<template>
  <span
    class="animated-number"
    :class="{ 'animated-number--flash': flashing }"
    :style="{ color: valueColor }"
  >
    {{ displayValue }}
  </span>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'

const props = withDefaults(defineProps<{
  value: number | string
  duration?: number
  precision?: number
  prefix?: string
  suffix?: string
  separator?: boolean
  valueColor?: string
  flashOnChange?: boolean
}>(), {
  duration: 600,
  precision: 0,
  prefix: '',
  suffix: '',
  separator: true,
  valueColor: 'inherit',
  flashOnChange: true,
})

const displayValue = ref('')
const flashing = ref(false)
let rafId: number | null = null

function formatNumber(num: number): string {
  const fixed = num.toFixed(props.precision)
  if (!props.separator) return fixed
  const parts = fixed.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return parts.join('.')
}

function parseValue(v: number | string): number {
  if (typeof v === 'number') return v
  const parsed = parseFloat(v.replace(/,/g, ''))
  return isNaN(parsed) ? 0 : parsed
}

function animate(from: number, to: number) {
  if (rafId) cancelAnimationFrame(rafId)
  const startTime = performance.now()

  function tick(now: number) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / props.duration, 1)
    const easeProgress = 1 - Math.pow(1 - progress, 3)
    const current = from + (to - from) * easeProgress
    displayValue.value = props.prefix + formatNumber(current) + props.suffix

    if (progress < 1) {
      rafId = requestAnimationFrame(tick)
    } else {
      displayValue.value = props.prefix + formatNumber(to) + props.suffix
    }
  }

  rafId = requestAnimationFrame(tick)
}

function triggerFlash() {
  if (!props.flashOnChange) return
  flashing.value = true
  setTimeout(() => {
    flashing.value = false
  }, 100)
}

const targetValue = computed(() => parseValue(props.value))

onMounted(() => {
  displayValue.value = props.prefix + formatNumber(targetValue.value) + props.suffix
})

watch(targetValue, (newVal, oldVal) => {
  if (oldVal === undefined) {
    displayValue.value = props.prefix + formatNumber(newVal) + props.suffix
    return
  }
  animate(oldVal, newVal)
  triggerFlash()
})
</script>

<style scoped>
.animated-number {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-variant-numeric: tabular-nums;
  transition: color 100ms ease;
}
.animated-number--flash {
  animation: number-flash 100ms ease;
}
@keyframes number-flash {
  0% {
    text-shadow: 0 0 8px currentColor;
  }
  100% {
    text-shadow: none;
  }
}
</style>
