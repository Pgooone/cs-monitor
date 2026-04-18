<template>
  <div>
    <!-- 筛选区 -->
    <n-card title="告警记录" class="mb-4">
      <n-space align="center" wrap>
        <n-select
          v-model:value="filterType"
          :options="alertTypeOptions"
          placeholder="告警类型"
          clearable
          style="width: 140px"
        />
        <n-date-picker
          v-model:formatted-value="filterStart"
          value-format="yyyy-MM-dd"
          type="date"
          placeholder="开始日期"
        />
        <n-date-picker
          v-model:formatted-value="filterEnd"
          value-format="yyyy-MM-dd"
          type="date"
          placeholder="结束日期"
        />
        <n-input
          v-model:value="filterName"
          placeholder="饰品名称搜索"
          style="width: 200px"
          clearable
        />
        <n-button type="primary" @click="handleSearch">查询</n-button>
        <n-button @click="handleReset">重置</n-button>
      </n-space>
    </n-card>

    <!-- 柱状图 -->
    <n-card title="告警趋势" class="mb-4">
      <div ref="chartRef" style="height: 260px" />
    </n-card>

    <!-- 列表 -->
    <n-card>
      <n-data-table
        :columns="columns"
        :data="store.items"
        :loading="store.loading"
        :pagination="pagination"
        size="small"
        striped
        @update:page="handlePageChange"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick, h } from 'vue'
import {
  NCard,
  NSpace,
  NSelect,
  NDatePicker,
  NInput,
  NButton,
  NDataTable,
  NTag,
} from 'naive-ui'
import type { DataTableColumns, PaginationProps } from 'naive-ui'
import { useAlertsStore } from '@/stores/alerts'
import type { AlertRecord } from '@/api'
import * as echarts from 'echarts'

const store = useAlertsStore()
const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const filterType = ref<string | null>(null)
const filterStart = ref<string | null>(null)
const filterEnd = ref<string | null>(null)
const filterName = ref('')

const alertTypeOptions = [
  { label: '价格暴涨', value: 'price_surge' },
  { label: '价格暴跌', value: 'price_drop' },
  { label: '价格变动', value: 'price_change' },
  { label: '数量变动', value: 'quantity_change' },
  { label: '综合变动', value: 'both' },
]

const typeMap: Record<string, string> = {
  price_surge: '价格暴涨',
  price_drop: '价格暴跌',
  price_change: '价格变动',
  quantity_change: '数量变动',
  both: '综合变动',
}

const typeTagMap: Record<string, string> = {
  price_surge: 'error',
  price_drop: 'warning',
  price_change: 'info',
  quantity_change: 'info',
  both: 'success',
}

function buildFilters() {
  const f: Record<string, string> = {}
  if (filterType.value) f.alert_type = filterType.value
  if (filterStart.value) f.start_date = filterStart.value
  if (filterEnd.value) f.end_date = filterEnd.value
  if (filterName.value.trim()) f.market_hash_name = filterName.value.trim()
  return f
}

function handleSearch() {
  store.setPage(1)
  store.fetchAlerts(buildFilters())
  store.fetchStats({
    start_date: filterStart.value || undefined,
    end_date: filterEnd.value || undefined,
  })
}

function handleReset() {
  filterType.value = null
  filterStart.value = null
  filterEnd.value = null
  filterName.value = ''
  store.setPage(1)
  store.fetchAlerts()
  store.fetchStats()
}

function handlePageChange(page: number) {
  store.setPage(page)
  store.fetchAlerts(buildFilters())
}

const pagination = computed<PaginationProps>(() => ({
  page: store.page,
  pageSize: store.limit,
  itemCount: store.total,
  showSizePicker: false,
}))

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

function updateChart() {
  if (!chartInstance || !store.stats) return
  const byDay = [...store.stats.by_day].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
  )
  const dates = byDay.map((d) => d.date)
  const counts = byDay.map((d) => d.count)

  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 30 },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        data: counts,
        itemStyle: { color: '#5470c6', borderRadius: [4, 4, 0, 0] },
      },
    ],
  })
}

watch(() => store.stats, () => {
  nextTick(updateChart)
})

const columns: DataTableColumns<AlertRecord> = [
  { title: '饰品', key: 'market_hash_name', ellipsis: { tooltip: true } },
  {
    title: '类型',
    key: 'alert_type',
    render(row) {
      return h(
        NTag,
        { type: (typeTagMap[row.alert_type] as any) || 'default', size: 'small' },
        { default: () => typeMap[row.alert_type] || row.alert_type },
      )
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

onMounted(() => {
  store.fetchAlerts()
  store.fetchStats()
  nextTick(initChart)
  window.addEventListener('resize', () => chartInstance?.resize())
})
</script>
