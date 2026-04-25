<template>
  <div>
    <page-header title="告警记录" />

    <!-- Tab + 筛选区 -->
    <n-card class="mb-4" :bordered="false">
      <n-tabs v-model:value="activeTab" type="line" @update:value="handleTabChange">
        <n-tab-pane name="normal" tab="普通监控告警" />
        <n-tab-pane name="extreme" tab="极致追踪告警" />
      </n-tabs>

      <div class="filter-row mt-4">
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
          clearable
        />
        <n-date-picker
          v-model:formatted-value="filterEnd"
          value-format="yyyy-MM-dd"
          type="date"
          placeholder="结束日期"
          clearable
        />
        <n-input
          v-model:value="filterName"
          placeholder="饰品名称搜索"
          style="width: 200px"
          clearable
        />
        <n-button type="primary" @click="handleSearch">
          <template #icon><SearchOutline /></template>
          查询
        </n-button>
        <n-button @click="handleReset">
          <template #icon><RefreshOutline /></template>
          重置
        </n-button>
      </div>
    </n-card>

    <!-- 柱状图 -->
    <n-card class="mb-4" title="告警趋势">
      <skeleton-chart v-if="statsLoading" />
      <div v-else ref="chartRef" style="height: 260px" />
    </n-card>

    <!-- 告警列表（按日期分组） -->
    <div v-if="loading" class="space-y-4">
      <skeleton-card v-for="i in 4" :key="i" />
    </div>

    <div v-else-if="groupedAlerts.length === 0" class="empty-state">
      <n-empty description="暂无告警记录" size="huge">
        <template #icon>
          <NotificationsOffOutline style="font-size: 48px; opacity: 0.4" />
        </template>
      </n-empty>
    </div>

    <div v-else class="alert-groups">
      <div
        v-for="group in groupedAlerts"
        :key="group.date"
        class="alert-group"
      >
        <div class="alert-group__header">
          <span class="alert-group__date">{{ group.date }}</span>
          <n-tag size="small" round>{{ group.items.length }} 条</n-tag>
        </div>
        <div class="alert-group__cards">
          <div
            v-for="alert in group.items"
            :key="alert.id"
            class="alert-card"
            @click="openDetail(alert)"
          >
            <div class="alert-card__left">
              <div class="alert-card__name">
                {{ alert.market_hash_name }}
                <span v-if="activeTab === 'extreme' && 'platform' in alert" class="alert-card__platform">
                  @{{ (alert as any).platform }}
                </span>
              </div>
              <div class="alert-card__meta">
                <n-tag :type="getTagType(alert.alert_type)" size="small" round>
                  {{ typeMap[alert.alert_type] || alert.alert_type }}
                </n-tag>
                <span class="alert-card__time">{{ formatTime(alert.notified_at) }}</span>
              </div>
            </div>
            <div class="alert-card__right">
              <div v-if="getAlertPrice(alert) != null" class="alert-card__price">
                ¥{{ getAlertPrice(alert)!.toFixed(2) }}
              </div>
              <div
                v-if="getAlertChangePercent(alert) != null"
                class="alert-card__change"
                :style="{ color: getAlertChangePercent(alert)! >= 0 ? colorUp : colorDown }"
              >
                {{ getAlertChangePercent(alert)! >= 0 ? '+' : '' }}{{ getAlertChangePercent(alert)!.toFixed(2) }}%
              </div>
            </div>
            <div class="alert-card__action">
              <n-button text type="primary" size="small" @click.stop="openDetail(alert)">
                查看 K 线
              </n-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="mt-4 flex justify-center">
        <n-pagination
          v-model:page="page"
          :page-count="Math.ceil(total / limit)"
          :page-size="limit"
          show-quick-jumper
          @update:page="handlePageChange"
        />
      </div>
    </div>

    <!-- 详情抽屉 -->
    <n-drawer v-model:show="drawerVisible" :width="520" placement="right">
      <n-drawer-content :title="detailTitle" closable>
        <div v-if="selectedAlert" class="detail-content">
          <div class="detail-section">
            <div class="detail-label">告警类型</div>
            <n-tag :type="getTagType(selectedAlert.alert_type)" size="medium" round>
              {{ typeMap[selectedAlert.alert_type] || selectedAlert.alert_type }}
            </n-tag>
          </div>

          <div class="detail-section grid-2">
            <div>
              <div class="detail-label">当前价格</div>
              <div class="detail-value">
                {{ getAlertPrice(selectedAlert) != null ? `¥${getAlertPrice(selectedAlert)!.toFixed(2)}` : '—' }}
              </div>
            </div>
            <div>
              <div class="detail-label">基准价格</div>
              <div class="detail-value">
                {{ (selectedAlert as any).baseline_price != null ? `¥${(selectedAlert as any).baseline_price.toFixed(2)}` : ((selectedAlert as any).prev_price != null ? `¥${(selectedAlert as any).prev_price.toFixed(2)}` : '—') }}
              </div>
            </div>
          </div>

          <div class="detail-section grid-2">
            <div>
              <div class="detail-label">变化幅度</div>
              <div
                class="detail-value"
                :style="{ color: (getAlertChangePercent(selectedAlert) || 0) >= 0 ? colorUp : colorDown }"
              >
                {{ getAlertChangePercent(selectedAlert) != null ? `${(getAlertChangePercent(selectedAlert)! >= 0 ? '+' : '')}${getAlertChangePercent(selectedAlert)!.toFixed(2)}%` : '—' }}
              </div>
            </div>
            <div>
              <div class="detail-label">通知时间</div>
              <div class="detail-value">{{ formatFullTime(selectedAlert.notified_at) }}</div>
            </div>
          </div>

          <n-divider />

          <div class="detail-section">
            <div class="detail-label">价格上下文</div>
            <div v-if="contextLoading" class="mt-2">
              <skeleton-table :rows="3" />
            </div>
            <div v-else-if="priceContext.length === 0" class="text-sm opacity-50 mt-2">
              暂无附近价格数据
            </div>
            <n-data-table
              v-else
              :columns="contextColumns"
              :data="priceContext"
              size="small"
              :bordered="false"
              :single-line="false"
              class="mt-2"
            />
          </div>

          <div class="detail-section mt-4">
            <n-button type="primary" block @click="goToKline(selectedAlert.market_hash_name)">
              查看 K 线详情
            </n-button>
          </div>
        </div>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NTabs,
  NTabPane,
  NSelect,
  NDatePicker,
  NInput,
  NButton,
  NTag,
  NEmpty,
  NPagination,
  NDrawer,
  NDrawerContent,
  NDivider,
  NDataTable,
} from 'naive-ui'
import { SearchOutline, RefreshOutline, NotificationsOffOutline } from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import { init } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { use as echartsUse } from 'echarts/core'
import type { ECharts } from 'echarts/core'
import api, { type AlertRecord, type ExtremeAlertRecord } from '@/api'

echartsUse([BarChart, GridComponent, TooltipComponent, CanvasRenderer])
import { useTheme } from '@/composables/useTheme'
import { toastError } from '@/composables/useToast'
import PageHeader from '@/components/layout/PageHeader.vue'
import SkeletonCard from '@/components/base/SkeletonCard.vue'
import SkeletonChart from '@/components/base/SkeletonChart.vue'
import SkeletonTable from '@/components/base/SkeletonTable.vue'

const router = useRouter()
const { colorUp, colorDown } = useTheme()

const activeTab = ref<'normal' | 'extreme'>('normal')
const items = ref<(AlertRecord | ExtremeAlertRecord)[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)
const loading = ref(false)
const statsLoading = ref(false)
const stats = ref<{ by_day: { date: string; count: number }[] } | null>(null)

const filterType = ref<string | null>(null)
const filterStart = ref<string | null>(null)
const filterEnd = ref<string | null>(null)
const filterName = ref('')

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: ECharts | null = null

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

const typeTagMap: Record<string, any> = {
  price_surge: 'error',
  price_drop: 'warning',
  price_change: 'info',
  quantity_change: 'info',
  both: 'success',
}

function getTagType(alertType: string): any {
  return typeTagMap[alertType] || 'default'
}

function getAlertPrice(alert: AlertRecord | ExtremeAlertRecord): number | null {
  if ('current_price' in alert) return alert.current_price
  if ('curr_price' in alert) return alert.curr_price
  return null
}

function getAlertChangePercent(alert: AlertRecord | ExtremeAlertRecord): number | null {
  if ('change_percent' in alert) return alert.change_percent
  if ('price_change_percent' in alert) return alert.price_change_percent
  return null
}

function buildFilters() {
  const f: Record<string, string> = {}
  if (filterType.value) f.alert_type = filterType.value
  if (filterStart.value) f.start_date = filterStart.value
  if (filterEnd.value) f.end_date = filterEnd.value
  if (filterName.value.trim()) f.market_hash_name = filterName.value.trim()
  return f
}

async function fetchData() {
  loading.value = true
  try {
    const filters = buildFilters()
    if (activeTab.value === 'normal') {
      const { data } = await api.alerts(page.value, limit.value, filters)
      items.value = data.items
      total.value = data.total
    } else {
      const { data } = await api.extremeAlerts(page.value, limit.value, filters)
      items.value = data.items
      total.value = data.total
    }
  } catch (e) {
    toastError('获取告警记录失败')
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  statsLoading.value = true
  try {
    if (activeTab.value === 'normal') {
      const { data } = await api.alertStats({
        start_date: filterStart.value || undefined,
        end_date: filterEnd.value || undefined,
      })
      stats.value = data
    } else {
      // extreme alerts stats not implemented yet, reuse normal for now
      const { data } = await api.alertStats({
        start_date: filterStart.value || undefined,
        end_date: filterEnd.value || undefined,
      })
      stats.value = data
    }
  } catch (e) {
    console.error(e)
  } finally {
    statsLoading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchData()
  fetchStats()
}

function handleReset() {
  filterType.value = null
  filterStart.value = null
  filterEnd.value = null
  filterName.value = ''
  page.value = 1
  fetchData()
  fetchStats()
}

function handlePageChange(p: number) {
  page.value = p
  fetchData()
}

function handleTabChange() {
  page.value = 1
  items.value = []
  total.value = 0
  fetchData()
  fetchStats()
}

const groupedAlerts = computed(() => {
  const groups: Record<string, (AlertRecord | ExtremeAlertRecord)[]> = {}
  for (const item of items.value) {
    const date = item.notified_at ? item.notified_at.slice(0, 10) : '未知日期'
    if (!groups[date]) groups[date] = []
    groups[date].push(item)
  }
  return Object.entries(groups)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([date, items]) => ({ date, items }))
})

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = init(chartRef.value)
  updateChart()
}

function updateChart() {
  if (!chartInstance || !stats.value) return
  const byDay = [...stats.value.by_day].sort(
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
        itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] },
      },
    ],
  })
}

watch(() => stats.value, () => {
  nextTick(updateChart)
})

// 详情抽屉
const drawerVisible = ref(false)
const selectedAlert = ref<AlertRecord | ExtremeAlertRecord | null>(null)
const priceContext = ref<any[]>([])
const contextLoading = ref(false)

const detailTitle = computed(() => {
  if (!selectedAlert.value) return '告警详情'
  return selectedAlert.value.market_hash_name
})

async function openDetail(alert: AlertRecord | ExtremeAlertRecord) {
  selectedAlert.value = alert
  drawerVisible.value = true
  contextLoading.value = true
  priceContext.value = []
  try {
    // 获取前后 10 条价格上下文
    const { data } = await api.priceHistory(alert.market_hash_name, 7)
    const alertTime = new Date(alert.notified_at).getTime()
    // 找出最接近告警时间的记录及其前后各 5 条
    const sorted = data.sort((a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime())
    let idx = sorted.findIndex((d) => new Date(d.recorded_at).getTime() >= alertTime)
    if (idx < 0) idx = sorted.length
    const start = Math.max(0, idx - 5)
    const end = Math.min(sorted.length, idx + 6)
    priceContext.value = sorted.slice(start, end).map((d) => ({
      ...d,
      _isAlert: new Date(d.recorded_at).getTime() === alertTime,
    }))
  } catch (e) {
    console.error(e)
  } finally {
    contextLoading.value = false
  }
}

function goToKline(name: string) {
  router.push({ name: 'ItemDetail', params: { name: encodeURIComponent(name) } })
}

function formatTime(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function formatFullTime(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const contextColumns: DataTableColumns<any> = [
  { title: '时间', key: 'recorded_at', width: 160 },
  { title: '平台', key: 'platform', width: 80 },
  {
    title: '价格',
    key: 'price',
    render(row) {
      return h('span', { style: { fontFamily: "'JetBrains Mono', monospace" } }, `¥${row.price.toFixed(2)}`)
    },
  },
]

onMounted(() => {
  fetchData()
  fetchStats()
  nextTick(initChart)
  window.addEventListener('resize', () => chartInstance?.resize())
})

onBeforeUnmount(() => {
  chartInstance?.dispose()
})
</script>

<style scoped>
.filter-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.empty-state {
  padding: 4rem 0;
  display: flex;
  justify-content: center;
}

.alert-groups {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.alert-group__header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0;
  background: var(--cs-bg-page);
  backdrop-filter: blur(8px);
}

.alert-group__date {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--cs-text-secondary);
}

.alert-group__cards {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.alert-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.125rem;
  background: var(--cs-bg-card);
  border: 1px solid var(--cs-border-light);
  border-radius: 0.875rem;
  cursor: pointer;
  transition: all var(--cs-transition-fast);
  box-shadow: var(--cs-shadow-sm);
}

.alert-card:hover {
  border-color: var(--cs-brand-primary);
  box-shadow: var(--cs-shadow-md);
  transform: translateY(-1px);
}

.alert-card__left {
  flex: 1;
  min-width: 0;
}

.alert-card__name {
  font-weight: 500;
  font-size: 0.9375rem;
  color: var(--cs-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-card__platform {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
  margin-left: 0.25rem;
}

.alert-card__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.375rem;
}

.alert-card__time {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
}

.alert-card__right {
  text-align: right;
  flex-shrink: 0;
}

.alert-card__price {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--cs-text-primary);
}

.alert-card__change {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  font-weight: 500;
}

.alert-card__action {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity var(--cs-transition-fast);
}

.alert-card:hover .alert-card__action {
  opacity: 1;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.detail-section.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
}

.detail-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--cs-text-primary);
  font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 639px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-row > * {
    width: 100% !important;
  }
  .alert-card__action {
    opacity: 1;
  }
  .detail-section.grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>
