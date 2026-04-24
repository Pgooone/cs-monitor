<template>
  <div ref="chartRef" class="portfolio-chart" />
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { init, use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'
import type { ECharts } from 'echarts/core'
import { getChartTheme } from '@/charts/theme'
import { brand } from '@/styles/tokens'

use([LineChart, GridComponent, TooltipComponent, SVGRenderer])

const props = defineProps<{
  data: { date: string; value: number }[]
  isDark: boolean
}>()

const chartRef = ref<HTMLDivElement>()
let chart: ECharts | null = null

function initChart() {
  if (!chartRef.value) return
  chart = init(chartRef.value, getChartTheme(props.isDark), { renderer: 'svg' })
  updateOption()
}

function updateOption() {
  if (!chart) return
  const xData = props.data.map(d => d.date.slice(5)) // MM-DD
  const yData = props.data.map(d => d.value)
  const color = props.isDark ? brand[400] : brand[500]

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        return `<div style="font-weight:600">${p.axisValue}</div>
                <div>总价值: ¥${Number(p.value).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</div>`
      },
    },
    grid: { left: '2%', right: '4%', bottom: '2%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xData,
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (v: number) => `¥${(v / 1000).toFixed(0)}k`,
      },
    },
    series: [{
      name: '组合价值',
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 3, color },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: props.isDark ? 'rgba(96,165,250,0.35)' : 'rgba(59,130,246,0.30)' },
            { offset: 1, color: props.isDark ? 'rgba(96,165,250,0.02)' : 'rgba(59,130,246,0.02)' },
          ],
        },
      },
      data: yData,
    }],
  }, true)
}

watch(() => props.data, updateOption, { deep: true })
watch(() => props.isDark, () => {
  if (chart) {
    chart.dispose()
    initChart()
  }
})

let resizeObserver: ResizeObserver | null = null
onMounted(() => {
  initChart()
  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(chartRef.value)
  }
})
onUnmounted(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<style scoped>
.portfolio-chart {
  width: 100%;
  height: 320px;
}
</style>
