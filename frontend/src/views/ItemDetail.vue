<template>
  <div>
    <page-header
      :title="displayName"
      :breadcrumbs="[
        { label: '监控清单', routeName: 'Watchlist' },
        { label: displayName },
      ]"
    >
      <template #actions>
        <n-button size="small" @click="$router.back()">返回</n-button>
      </template>
    </page-header>

    <!-- 骨架屏 -->
    <template v-if="loading">
      <div class="item-hero skeleton-hero">
        <div class="skeleton-line" style="width: 60%; height: 2rem;" />
        <div class="skeleton-line" style="width: 40%; height: 1rem; margin-top: 0.75rem;" />
        <div class="skeleton-line" style="width: 30%; height: 3rem; margin-top: 1rem;" />
      </div>
      <SkeletonChart />
      <div class="mt-4">
        <SkeletonTable :rows="5" :columns="5" />
      </div>
    </template>

    <!-- 顶部信息栏 -->
    <template v-else>
    <div class="item-hero">
      <div class="item-hero__left">
        <div class="item-hero__title-row">
          <SteamItemImage
            :market-hash-name="marketHashName"
            :icon-url="iconUrl"
            :alt="displayName"
            class-name="item-hero__emoji-img"
          />
          <h1 class="item-hero__title">{{ displayName }}</h1>
          <span
            v-if="wearLabel"
            class="item-hero__wear"
            :class="wearClass"
          >{{ wearLabel }}</span>
        </div>
        <div class="item-hero__platforms">
          <n-tag
            v-for="p in platformPrices"
            :key="p.platform"
            size="small"
            :type="p.price === minPlatformPrice ? 'primary' : 'default'"
            :bordered="false"
            class="item-hero__platform-tag"
          >
            {{ p.platform }} ¥{{ p.price.toFixed(0) }}
          </n-tag>
          <span v-if="!platformPrices.length" class="text-gray-400 text-sm">暂无平台数据</span>
        </div>
      </div>
      <div class="item-hero__right">
        <div class="item-hero__price font-mono-num">
          <AnimatedNumber
            v-if="currentPrice != null"
            :value="currentPrice"
            :precision="2"
            prefix="¥"
          />
          <span v-else>—</span>
        </div>
        <div class="item-hero__badges">
          <span
            v-if="change24h != null"
            class="item-hero__badge"
            :class="change24h >= 0 ? 'up' : 'down'"
            :style="{ color: change24h >= 0 ? colorUp : colorDown }"
          >
            24h {{ change24h >= 0 ? '+' : '' }}{{ change24h.toFixed(2) }}%
          </span>
          <span
            v-if="change7d != null"
            class="item-hero__badge"
            :class="change7d >= 0 ? 'up' : 'down'"
            :style="{ color: change7d >= 0 ? colorUp : colorDown }"
          >
            7d {{ change7d >= 0 ? '+' : '' }}{{ change7d.toFixed(2) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- 趋势标签 -->
    <n-card :bordered="false" size="small" class="trend-bar">
      <n-space align="center">
        <n-tag v-if="trendLabel" :type="trendTagType as any" size="large">{{ trendLabel }}</n-tag>
        <n-tag v-if="ma5Latest != null" type="default" size="small">MA5: ¥{{ ma5Latest.toFixed(2) }}</n-tag>
        <n-tag v-if="ma10Latest != null" type="default" size="small">MA10: ¥{{ ma10Latest.toFixed(2) }}</n-tag>
        <n-tag v-if="ma20Latest != null" type="default" size="small">MA20: ¥{{ ma20Latest.toFixed(2) }}</n-tag>
      </n-space>
    </n-card>

    <!-- 图表控制栏 -->
    <n-card :bordered="false" size="small" class="chart-controls">
      <div class="chart-controls__row">
        <!-- 图表类型 -->
        <n-radio-group v-model:value="chartType" size="small">
          <n-radio-button value="line">价格走势</n-radio-button>
          <n-radio-button value="kline">K线图</n-radio-button>
        </n-radio-group>

        <!-- 时间粒度：价格走势 -->
        <n-radio-group v-if="chartType === 'line'" v-model:value="historyDays" size="small">
          <n-radio-button :value="7">7天</n-radio-button>
          <n-radio-button :value="30">30天</n-radio-button>
          <n-radio-button :value="90">90天</n-radio-button>
        </n-radio-group>

        <!-- 时间粒度：K线 -->
        <n-radio-group v-if="chartType === 'kline'" v-model:value="klinePeriod" size="small">
          <n-radio-button :value="1">时K</n-radio-button>
          <n-radio-button :value="2">日K</n-radio-button>
          <n-radio-button :value="3">周K</n-radio-button>
        </n-radio-group>

        <!-- 平台对比（价格走势时） -->
        <n-checkbox-group
          v-if="chartType === 'line' && availablePlatforms.length > 1"
          v-model:value="selectedPlatforms"
          size="small"
        >
          <n-space>
            <n-checkbox
              v-for="p in availablePlatforms"
              :key="p"
              :value="p"
              :label="p"
            />
          </n-space>
        </n-checkbox-group>

        <!-- 技术指标 -->
        <n-checkbox-group v-model:value="activeIndicators" size="small">
          <n-space>
            <n-checkbox value="ma5" label="MA5" />
            <n-checkbox value="ma10" label="MA10" />
            <n-checkbox value="ma30" label="MA30" />
            <n-checkbox v-if="chartType === 'kline'" value="volume" label="成交量" />
          </n-space>
        </n-checkbox-group>

        <!-- 导出 -->
        <n-space>
          <n-button size="tiny" text @click="exportPNG">导出 PNG</n-button>
          <n-button size="tiny" text @click="exportCSV">导出 CSV</n-button>
        </n-space>
      </div>
    </n-card>

    <!-- 图表 -->
    <n-card :bordered="false" size="small" class="chart-card">
      <div ref="chartRef" class="chart-container" />
      <n-empty v-if="chartEmpty" description="暂无数据" />
    </n-card>

    <!-- 告警历史 -->
    <n-card title="告警历史" :bordered="false" size="small" class="mt-4">
      <n-data-table
        :columns="alertColumns"
        :data="alerts"
        :pagination="{ pageSize: 10 }"
        size="small"
        striped
      />
    </n-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  NCard,
  NTag,
  NButton,
  NSpace,
  NDataTable,
  NRadioGroup,
  NRadioButton,
  NCheckbox,
  NCheckboxGroup,
  NEmpty,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { init, use } from 'echarts/core'
import { LineChart, CandlestickChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkPointComponent,
  TitleComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ECharts } from 'echarts/core'
import api, {
  type PriceHistoryItem,
  type PlatformPriceItem,
  type AlertRecord,
  type KlineDataItem,
  type TrendAnalysisResponse,
} from '@/api'
import PageHeader from '@/components/layout/PageHeader.vue'
import SkeletonChart from '@/components/base/SkeletonChart.vue'
import SkeletonTable from '@/components/base/SkeletonTable.vue'
import AnimatedNumber from '@/components/base/AnimatedNumber.vue'
import SteamItemImage from '@/components/business/SteamItemImage.vue'
import { getChartTheme } from '@/charts/theme'
import { useTheme } from '@/composables/useTheme'

use([
  LineChart,
  CandlestickChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkPointComponent,
  TitleComponent,
  CanvasRenderer,
])

const route = useRoute()
const marketHashName = computed(() => decodeURIComponent(route.params.name as string))
const displayNameValue = ref<string | null>(null)
const displayName = computed(() => displayNameValue.value || marketHashName.value)
const iconUrl = ref<string | null>(null)
const { isDark, colorUp, colorDown } = useTheme()

const loading = ref(false)
const currentPrice = ref<number | null>(null)
const change24h = ref<number | null>(null)
const change7d = ref<number | null>(null)
const platformPrices = ref<PlatformPriceItem[]>([])
const priceHistory = ref<PriceHistoryItem[]>([])
const alerts = ref<AlertRecord[]>([])
const historyDays = ref(7)
const chartType = ref<'line' | 'kline'>('line')
const klinePeriod = ref(2)
const klineData = ref<KlineDataItem[]>([])
const trendData = ref<TrendAnalysisResponse | null>(null)
const selectedPlatforms = ref<string[]>([])
const activeIndicators = ref<string[]>(['ma5', 'ma10'])
const platformHistory = ref<Record<string, PriceHistoryItem[]>>({})

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: ECharts | null = null

// 品相解析
const wearMap: Record<string, string> = {
  'Factory New': '崭新出厂',
  'Minimal Wear': '略有磨损',
  'Field-Tested': '久经沙场',
  'Well-Worn': '破损不堪',
  'Battle-Scarred': '战痕累累',
}

const wearLabel = computed(() => {
  const match = marketHashName.value.match(/\(([^)]+)\)/)
  if (!match) return ''
  return wearMap[match[1]] || match[1]
})

const wearClass = computed(() => {
  const match = marketHashName.value.match(/\(([^)]+)\)/)
  if (!match) return ''
  const map: Record<string, string> = {
    'Factory New': 'wear--fn',
    'Minimal Wear': 'wear--mw',
    'Field-Tested': 'wear--ft',
    'Well-Worn': 'wear--ww',
    'Battle-Scarred': 'wear--bs',
  }
  return map[match[1]] || ''
})

const minPlatformPrice = computed(() => {
  if (!platformPrices.value.length) return undefined
  return Math.min(...platformPrices.value.map((p) => p.price))
})

const trendLabel = computed(() => {
  const map: Record<string, string> = {
    surge: '📈 连涨趋势',
    drop: '📉 连跌趋势',
    oscillate: '🔄 震荡整理',
  }
  return trendData.value ? map[trendData.value.trend] || '' : ''
})

const trendTagType = computed(() => {
  const map: Record<string, string> = {
    surge: 'error',
    drop: 'success',
    oscillate: 'warning',
  }
  return trendData.value ? map[trendData.value.trend] || 'default' : 'default'
})

const ma5Latest = computed(() => {
  if (!trendData.value?.ma5) return null
  const vals = trendData.value.ma5.filter((v): v is number => v != null)
  return vals.length ? vals[vals.length - 1] : null
})

const ma10Latest = computed(() => {
  if (!trendData.value?.ma10) return null
  const vals = trendData.value.ma10.filter((v): v is number => v != null)
  return vals.length ? vals[vals.length - 1] : null
})

const ma20Latest = computed(() => {
  if (!trendData.value?.ma20) return null
  const vals = trendData.value.ma20.filter((v): v is number => v != null)
  return vals.length ? vals[vals.length - 1] : null
})

const chartEmpty = computed(() => {
  if (chartType.value === 'kline') return !klineData.value.length
  return !priceHistory.value.length
})

const availablePlatforms = computed(() =>
  [...new Set(priceHistory.value.map((p) => p.platform))].sort(),
)

function initChart() {
  if (!chartRef.value || chartEmpty.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = init(chartRef.value, getChartTheme(isDark.value), {
    renderer: 'canvas',
  })

  if (chartType.value === 'kline') {
    initKlineChart()
  } else {
    initLineChart()
  }
}

function calcMA(data: number[], dayCount: number): (number | null)[] {
  const result: (number | null)[] = []
  for (let i = 0; i < data.length; i++) {
    if (i < dayCount - 1) {
      result.push(null)
      continue
    }
    let sum = 0
    for (let j = 0; j < dayCount; j++) {
      sum += data[i - j]
    }
    result.push(+(sum / dayCount).toFixed(2))
  }
  return result
}

function initLineChart() {
  if (!chartInstance) return

  const series: any[] = []
  const xData: string[] = []

  if (selectedPlatforms.value.length <= 1) {
    // 单线：显示默认价格历史
    const sorted = [...priceHistory.value].sort(
      (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime(),
    )
    const dates = sorted.map((item) =>
      new Date(item.recorded_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
    )
    const prices = sorted.map((item) => item.price)
    xData.push(...dates)

    series.push({
      name: '价格',
      type: 'line',
      data: prices,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2 },
      areaStyle: { opacity: 0.1 },
    })

    // MA
    if (activeIndicators.value.includes('ma5')) {
      series.push({
        name: 'MA5',
        type: 'line',
        data: calcMA(prices, 5),
        smooth: true,
        showSymbol: false,
        lineStyle: { opacity: 0.8, width: 1, type: 'dashed' },
      })
    }
    if (activeIndicators.value.includes('ma10')) {
      series.push({
        name: 'MA10',
        type: 'line',
        data: calcMA(prices, 10),
        smooth: true,
        showSymbol: false,
        lineStyle: { opacity: 0.8, width: 1, type: 'dashed' },
      })
    }
    if (activeIndicators.value.includes('ma30')) {
      series.push({
        name: 'MA30',
        type: 'line',
        data: calcMA(prices, 30),
        smooth: true,
        showSymbol: false,
        lineStyle: { opacity: 0.8, width: 1, type: 'dashed' },
      })
    }
  } else {
    // 多平台对比：为每个选中的平台获取数据
    const platformData: Record<string, { dates: string[]; prices: number[] }> = {}

    for (const platform of selectedPlatforms.value) {
      const hist = platformHistory.value[platform] || []
      const sorted = [...hist].sort(
        (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime(),
      )
      if (!sorted.length) continue
      const dates = sorted.map((item) =>
        new Date(item.recorded_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
      )
      const prices = sorted.map((item) => item.price)
      platformData[platform] = { dates, prices }
      if (!xData.length) xData.push(...dates)
    }

    for (const [platform, data] of Object.entries(platformData)) {
      series.push({
        name: platform,
        type: 'line',
        data: data.prices,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2 },
      })
    }
  }

  // 告警标注
  const markPoints = alerts.value
    .filter((a) => a.current_price != null)
    .map((a) => ({
      name: a.alert_type,
      coord: [0, a.current_price!],
      value: a.alert_type === 'price_surge' ? '暴涨' : a.alert_type === 'price_drop' ? '暴跌' : '告警',
      itemStyle: { color: a.alert_type === 'price_surge' ? colorUp.value : colorDown.value },
      symbol: 'triangle',
      symbolSize: 12,
      symbolRotate: a.alert_type === 'price_drop' ? 180 : 0,
    }))

  if (markPoints.length && series.length) {
    series[0].markPoint = {
      data: markPoints,
      label: { show: false },
      symbolOffset: [0, -10],
    }
  }

  const option = {
    tooltip: { trigger: 'axis' },
    legend: series.length > 1 ? { bottom: 0 } : undefined,
    grid: { left: '3%', right: '4%', bottom: series.length > 1 ? '12%' : '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: xData },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (value: number) => `¥${value.toFixed(0)}` },
    },
    series,
  }

  chartInstance.setOption(option, true)
}

function initKlineChart() {
  if (!chartInstance) return
  const raw = klineData.value
  // 后端返回 timestamp（Unix 秒），前端需要 date 字符串
  const dates = raw.map((d) => {
    if (d.date) return d.date
    // timestamp 转日期字符串
    const ts = (d as any).timestamp
    if (ts) {
      return new Date(ts * 1000).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    }
    return ''
  })
  const data = raw.map((d) => [d.open, d.close, d.low, d.high])
  const volumes = raw.map((d, i) => [i, d.volume || 0, d.close > d.open ? 1 : -1])
  const closePrices = raw.map((d) => d.close)

  const maSeries: any[] = []
  if (activeIndicators.value.includes('ma5')) {
    maSeries.push({
      name: 'MA5',
      type: 'line',
      data: calcMA(closePrices, 5),
      smooth: true,
      showSymbol: false,
      lineStyle: { opacity: 0.8, width: 1 },
    })
  }
  if (activeIndicators.value.includes('ma10')) {
    maSeries.push({
      name: 'MA10',
      type: 'line',
      data: calcMA(closePrices, 10),
      smooth: true,
      showSymbol: false,
      lineStyle: { opacity: 0.8, width: 1 },
    })
  }
  if (activeIndicators.value.includes('ma30')) {
    maSeries.push({
      name: 'MA30',
      type: 'line',
      data: calcMA(closePrices, 30),
      smooth: true,
      showSymbol: false,
      lineStyle: { opacity: 0.8, width: 1 },
    })
  }

  const hasVolume = activeIndicators.value.includes('volume')

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: { bottom: 0 },
    grid: hasVolume
      ? [
          { left: '3%', right: '4%', top: '10%', height: '55%' },
          { left: '3%', right: '4%', top: '72%', height: '16%' },
        ]
      : [{ left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true }],
    xAxis: hasVolume
      ? [
          { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
          { type: 'category', data: dates, gridIndex: 1 },
        ]
      : { type: 'category', data: dates, gridIndex: 0 },
    yAxis: hasVolume
      ? [
          {
            scale: true,
            gridIndex: 0,
            axisLabel: { formatter: (v: number) => `¥${v.toFixed(0)}` },
          },
          {
            scale: true,
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false },
          },
        ]
      : {
          scale: true,
          gridIndex: 0,
          axisLabel: { formatter: (v: number) => `¥${v.toFixed(0)}` },
        },
    dataZoom: [{ type: 'inside', xAxisIndex: hasVolume ? [0, 1] : [0] }],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data,
        itemStyle: {
          color: colorUp.value,
          color0: colorDown.value,
          borderColor: colorUp.value,
          borderColor0: colorDown.value,
        },
        ...(hasVolume ? { xAxisIndex: 0, yAxisIndex: 0 } : {}),
      },
      ...maSeries.map((s) => (hasVolume ? { ...s, xAxisIndex: 0, yAxisIndex: 0 } : s)),
      ...(hasVolume
        ? [
            {
              name: '成交量',
              type: 'bar',
              xAxisIndex: 1,
              yAxisIndex: 1,
              data: volumes,
              itemStyle: {
                color: (params: any) => (params.value[2] > 0 ? colorUp.value : colorDown.value),
              },
            },
          ]
        : []),
    ],
  }

  chartInstance.setOption(option, true)
}

function handleResize() {
  chartInstance?.resize()
}

async function loadData() {
  const name = marketHashName.value
  if (!name) return

  loading.value = true
  try {
    // trends 单独请求，数据不足时会 500，不应阻塞整个页面
    api.trends(name, 30).then(
      (res) => { trendData.value = res.data },
      () => { trendData.value = null },
    )

    const reqs: any[] = [
      api.priceHistory(name, historyDays.value),
      api.platformPrices(name),
      api.alerts(1, 50, { market_hash_name: name }),
      api.watchlist(),
    ]
    if (chartType.value === 'kline') {
      reqs.push(api.kline(name, klinePeriod.value))
    }
    const results = await Promise.all(reqs)

    priceHistory.value = results[0].data
    platformPrices.value = results[1].data
    alerts.value = results[2].data.items
    if (chartType.value === 'kline' && results[4]) {
      klineData.value = results[4].data.data || []
    }

    // 从 watchlist 获取 display_name 和 icon_url
    const watchlistData = results[3]?.data
    if (Array.isArray(watchlistData)) {
      const matched = watchlistData.find((w: any) => w.market_hash_name === name)
      if (matched?.display_name) {
        displayNameValue.value = matched.display_name
      }
      if (matched?.icon_url) {
        iconUrl.value = matched.icon_url
      }
    }

    // 当前价
    if (results[1].data.length) {
      currentPrice.value = results[1].data[0].price
    } else if (results[0].data.length) {
      currentPrice.value = results[0].data[0].price
    } else {
      currentPrice.value = null
    }

    // 计算 24h 和 7d 变化
    const sorted = [...priceHistory.value].sort(
      (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime(),
    )
    if (sorted.length && currentPrice.value != null) {
      const now = Date.now()
      const dayMs = 24 * 60 * 60 * 1000

      // 24h 变化：找最接近 24h 前的记录
      const p24h = sorted.find((p) => {
        const t = new Date(p.recorded_at).getTime()
        return now - t >= dayMs * 0.8 && now - t <= dayMs * 1.2
      })
      if (p24h) {
        change24h.value = ((currentPrice.value - p24h.price) / p24h.price) * 100
      } else {
        change24h.value = null
      }

      // 7d 变化：找最早记录（约7天前）
      const p7d = sorted[0]
      if (p7d && now - new Date(p7d.recorded_at).getTime() >= dayMs * 5) {
        change7d.value = ((currentPrice.value - p7d.price) / p7d.price) * 100
      } else {
        change7d.value = null
      }
    } else {
      change24h.value = null
      change7d.value = null
    }

    // 平台对比数据
    if (selectedPlatforms.value.length > 1) {
      const platformReqs = selectedPlatforms.value.map((platform) =>
        api.priceHistory(name, historyDays.value, platform),
      )
      const platformResults = await Promise.all(platformReqs)
      platformHistory.value = {}
      selectedPlatforms.value.forEach((platform, i) => {
        platformHistory.value[platform] = platformResults[i]?.data || []
      })
    }

    // 初始化图表
    initChart()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function exportPNG() {
  if (!chartInstance) return
  const url = chartInstance.getDataURL({ type: 'png', pixelRatio: 2 })
  const a = document.createElement('a')
  a.href = url
  a.download = `${marketHashName.value}-${chartType.value}.png`
  a.click()
}

function exportCSV() {
  let rows: string[][] = []
  if (chartType.value === 'kline') {
    rows = [['日期', '开盘', '收盘', '最高', '最低', '成交量']]
    klineData.value.forEach((d) => {
      rows.push([d.date, String(d.open), String(d.close), String(d.high), String(d.low), String(d.volume)])
    })
  } else {
    rows = [['时间', '平台', '价格']]
    priceHistory.value.forEach((p) => {
      rows.push([p.recorded_at, p.platform, String(p.price)])
    })
  }
  const csv = rows.map((r) => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${marketHashName.value}-${chartType.value}.csv`
  a.click()
  URL.revokeObjectURL(url)
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

watch(chartType, () => {
  loadData()
})

watch(klinePeriod, () => {
  if (chartType.value === 'kline') {
    loadData()
  }
})

watch(selectedPlatforms, () => {
  if (chartType.value === 'line') {
    loadData()
  }
})

watch(activeIndicators, () => {
  initChart()
})

watch(isDark, () => {
  if (chartInstance) {
    chartInstance.dispose()
    initChart()
  }
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

<style scoped>
.item-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--n-card-color, #fff);
  border-radius: 1rem;
  border: 1px solid rgba(0, 0, 0, 0.06);
  margin-bottom: 1rem;
}
html.dark .item-hero {
  border-color: rgba(255, 255, 255, 0.06);
}

.item-hero__left {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
}
.item-hero__title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.item-hero__emoji {
  font-size: 2rem;
}
.item-hero__emoji-img {
  width: 3rem;
  height: 3rem;
  object-fit: contain;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.2));
}
.item-hero__title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
  word-break: break-word;
}
.item-hero__wear {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
}
.wear--fn {
  background: #dcfce7;
  color: #166534;
}
.wear--mw {
  background: #dbeafe;
  color: #1e40af;
}
.wear--ft {
  background: #fef3c7;
  color: #92400e;
}
.wear--ww {
  background: #ffedd5;
  color: #9a3412;
}
.wear--bs {
  background: #fee2e2;
  color: #991b1b;
}
html.dark .wear--fn {
  background: #14532d;
  color: #86efac;
}
html.dark .wear--mw {
  background: #1e3a8a;
  color: #93c5fd;
}
html.dark .wear--ft {
  background: #78350f;
  color: #fcd34d;
}
html.dark .wear--ww {
  background: #7c2d12;
  color: #fdba74;
}
html.dark .wear--bs {
  background: #7f1d1d;
  color: #fca5a5;
}

.item-hero__platforms {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}
.item-hero__platform-tag {
  font-family: 'JetBrains Mono', monospace;
}

.item-hero__right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}
.item-hero__price {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: var(--n-text-color-1);
}
.item-hero__badges {
  display: flex;
  gap: 0.5rem;
}
.item-hero__badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.25rem 0.625rem;
  border-radius: 0.375rem;
  background: rgba(0, 0, 0, 0.04);
}
html.dark .item-hero__badge {
  background: rgba(255, 255, 255, 0.08);
}

.trend-bar {
  margin-bottom: 1rem;
}

.chart-controls {
  margin-bottom: 0.5rem;
}
.chart-controls__row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.chart-card {
  overflow: hidden;
}
.chart-container {
  width: 100%;
  height: 480px;
}

.mt-4 {
  margin-top: 1rem;
}

/* 骨架屏 */
.skeleton-hero {
  border-radius: 1rem;
  padding: 1.25rem;
  background: var(--n-card-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  margin-bottom: 1rem;
}
html.dark .skeleton-hero {
  border-color: rgba(255, 255, 255, 0.06);
}
.skeleton-line {
  height: 0.875rem;
  border-radius: 0.25rem;
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.06) 25%,
    rgba(0, 0, 0, 0.10) 50%,
    rgba(0, 0, 0, 0.06) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}
html.dark .skeleton-line {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.08) 25%,
    rgba(255, 255, 255, 0.14) 50%,
    rgba(255, 255, 255, 0.08) 75%
  );
  background-size: 200% 100%;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
