<template>
  <div>
    <n-space align="center" class="mb-4">
      <n-button size="small" @click="$router.back()">返回</n-button>
      <h2 class="m-0 text-xl">{{ displayName }}</h2>
    </n-space>

    <n-spin :show="loading">
      <!-- 统计卡片 -->
      <n-grid :x-gap="16" :y-gap="16" :cols="3">
        <n-gi>
          <n-card>
            <n-statistic label="当前价格">
              <template #prefix>
                <span class="text-blue-500 mr-2">💰</span>
              </template>
              <span>{{ currentPrice != null ? `¥${currentPrice.toFixed(2)}` : '—' }}</span>
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="均价">
              <template #prefix>
                <span class="text-green-500 mr-2">📊</span>
              </template>
              <span>{{ avgPrice != null ? `¥${avgPrice.toFixed(2)}` : '—' }}</span>
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="波动率">
              <template #prefix>
                <span class="text-orange-500 mr-2">📈</span>
              </template>
              <span :class="changeClass">{{ changeText }}</span>
            </n-statistic>
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 各平台价格对比 -->
      <n-card title="各平台价格对比" class="mt-4">
        <n-grid :x-gap="16" :y-gap="16" :cols="platformPrices.length || 1">
          <n-gi v-for="p in platformPrices" :key="p.platform">
            <n-card embedded>
              <n-statistic :label="p.platform" :value="`¥${p.price.toFixed(2)}`" />
              <n-text depth="3" class="text-xs">{{ formatDate(p.recorded_at) }}</n-text>
            </n-card>
          </n-gi>
          <n-gi v-if="!platformPrices.length">
            <n-empty description="暂无平台价格数据" />
          </n-gi>
        </n-grid>
      </n-card>

      <!-- 价格走势图 -->
      <n-card title="价格走势" class="mt-4">
        <template #header-extra>
          <n-radio-group v-model:value="historyDays" size="small">
            <n-radio-button :value="7">7天</n-radio-button>
            <n-radio-button :value="30">30天</n-radio-button>
          </n-radio-group>
        </template>
        <div ref="chartRef" style="width: 100%; height: 360px;" />
        <n-empty v-if="!priceHistory.length" description="暂无历史价格数据" />
      </n-card>

      <!-- 告警历史 -->
      <n-card title="告警历史" class="mt-4">
        <n-data-table
          :columns="alertColumns"
          :data="alerts"
          :pagination="{ pageSize: 10 }"
          size="small"
          striped
        />
      </n-card>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  NSpin,
  NGrid,
  NGi,
  NCard,
  NStatistic,
  NText,
  NButton,
  NSpace,
  NDataTable,
  NRadioGroup,
  NRadioButton,
  NEmpty,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import * as echarts from 'echarts'
import api, { type PriceHistoryItem, type PlatformPriceItem, type AlertRecord } from '@/api'

const route = useRoute()
const marketHashName = computed(() => decodeURIComponent(route.params.name as string))
const displayName = computed(() => marketHashName.value)

const loading = ref(false)
const currentPrice = ref<number | null>(null)
const avgPrice = ref<number | null>(null)
const changePercent = ref<number | null>(null)
const platformPrices = ref<PlatformPriceItem[]>([])
const priceHistory = ref<PriceHistoryItem[]>([])
const alerts = ref<AlertRecord[]>([])
const historyDays = ref(7)

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const changeText = computed(() => {
  if (changePercent.value == null) return '—'
  const sign = changePercent.value >= 0 ? '+' : ''
  return `${sign}${changePercent.value.toFixed(2)}%`
})

const changeClass = computed(() => {
  if (changePercent.value == null) return ''
  return changePercent.value >= 0 ? 'text-red-500' : 'text-green-500'
})

function formatDate(dateStr: string | null) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString()
}

function initChart() {
  if (!chartRef.value || !priceHistory.value.length) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)

  const sorted = [...priceHistory.value].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime(),
  )

  const dates = sorted.map((item) =>
    new Date(item.recorded_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
  )
  const prices = sorted.map((item) => item.price)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => `¥${value.toFixed(0)}`,
      },
    },
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        smooth: true,
        areaStyle: {
          opacity: 0.1,
        },
      },
    ],
  }

  chartInstance.setOption(option)
}

function handleResize() {
  chartInstance?.resize()
}

async function loadData() {
  const name = marketHashName.value
  if (!name) return

  loading.value = true
  try {
    const [historyRes, platformRes, alertsRes] = await Promise.all([
      api.priceHistory(name, historyDays.value),
      api.platformPrices(name),
      api.alerts(1, 50, { market_hash_name: name }),
    ])

    priceHistory.value = historyRes.data
    platformPrices.value = platformRes.data
    alerts.value = alertsRes.data.items

    if (platformRes.data.length) {
      currentPrice.value = platformRes.data[0].price
    } else if (historyRes.data.length) {
      currentPrice.value = historyRes.data[0].price
    } else {
      currentPrice.value = null
    }

    if (historyRes.data.length) {
      const total = historyRes.data.reduce((sum, item) => sum + item.price, 0)
      avgPrice.value = total / historyRes.data.length
      if (currentPrice.value != null) {
        changePercent.value = ((currentPrice.value - avgPrice.value) / avgPrice.value) * 100
      }
    } else {
      avgPrice.value = null
      changePercent.value = null
    }

    initChart()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const alertColumns: DataTableColumns<AlertRecord> = [
  {
    title: '类型',
    key: 'alert_type',
    render(row) {
      const typeMap: Record<string, string> = {
        price_surge: '📈 价格暴涨',
        price_drop: '📉 价格暴跌',
        both: '🔔 价格+数量变动',
        price_change: '💰 价格变动',
        quantity_change: '📦 数量变动',
      }
      return typeMap[row.alert_type] || row.alert_type
    },
  },
  {
    title: '当前价',
    key: 'current_price',
    render(row) {
      if (row.current_price == null) return '—'
      return `¥${row.current_price.toFixed(2)}`
    },
  },
  {
    title: '基准价',
    key: 'baseline_price',
    render(row) {
      if (row.baseline_price == null) return '—'
      return `¥${row.baseline_price.toFixed(2)}`
    },
  },
  {
    title: '波动',
    key: 'change_percent',
    render(row) {
      if (row.change_percent == null) return '—'
      const sign = row.change_percent >= 0 ? '+' : ''
      return `${sign}${row.change_percent.toFixed(2)}%`
    },
  },
  { title: '时间', key: 'notified_at' },
]

watch(historyDays, () => {
  loadData()
})

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>
