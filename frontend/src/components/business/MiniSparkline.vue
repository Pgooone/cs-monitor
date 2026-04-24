<template>
  <svg
    :width="width"
    :height="height"
    :viewBox="`0 0 ${width} ${height}`"
    preserveAspectRatio="none"
    class="mini-sparkline"
  >
    <defs>
      <linearGradient :id="gradId" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" :stop-color="color" stop-opacity="0.35" />
        <stop offset="100%" :stop-color="color" stop-opacity="0.02" />
      </linearGradient>
    </defs>
    <path
      :d="areaPath"
      :fill="`url(#${gradId})`"
    />
    <path
      :d="linePath"
      fill="none"
      :stroke="color"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  data: number[]
  width?: number
  height?: number
  color?: string
}>(), {
  width: 120,
  height: 40,
  color: '#3b82f6',
})

const gradId = computed(() => `spgrad-${Math.random().toString(36).slice(2, 8)}`)

const linePath = computed(() => {
  const data = props.data
  if (data.length < 2) return ''
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const stepX = props.width / (data.length - 1)
  const padY = 4
  const h = props.height - padY * 2

  return data.map((v, i) => {
    const x = i * stepX
    const y = props.height - padY - ((v - min) / range) * h
    return `${i === 0 ? 'M' : 'L'}${x},${y}`
  }).join(' ')
})

const areaPath = computed(() => {
  if (!linePath.value) return ''
  return `${linePath.value} L${props.width},${props.height} L0,${props.height} Z`
})
</script>

<style scoped>
.mini-sparkline {
  display: block;
}
</style>
