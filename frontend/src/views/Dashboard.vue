<template>
  <div>
    <n-spin :show="dashboard.loading">
      <!-- 统计卡片 -->
      <n-grid :x-gap="16" :y-gap="16" :cols="4">
        <n-gi>
          <n-card>
            <n-statistic label="监控清单" :value="dashboard.activeWatchlistCount">
              <template #prefix>
                <span class="text-blue-500 mr-2">📋</span>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="极致追踪" :value="dashboard.extremeTrackCount">
              <template #prefix>
                <span class="text-purple-500 mr-2">🎯</span>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="今日告警" :value="dashboard.todayAlertCount">
              <template #prefix>
                <span class="text-red-500 mr-2">🔔</span>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="价格记录" :value="dashboard.latestPriceCount">
              <template #prefix>
                <span class="text-green-500 mr-2">💰</span>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 价格概览表 -->
      <n-card title="监控价格概览" class="mt-4">
        <n-data-table
          :columns="priceColumns"
          :data="dashboard.watchlist"
          :pagination="{ pageSize: 10 }"
          size="small"
          striped
        />
      </n-card>

      <!-- 最近告警 -->
      <n-card title="最近告警" class="mt-4">
        <n-data-table
          :columns="alertColumns"
          :data="dashboard.alerts"
          :pagination="false"
          size="small"
          striped
        />
      </n-card>

      <n-divider />
      <n-text depth="3">最后更新: {{ dashboard.lastUpdate }}</n-text>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import {
  NSpin,
  NGrid,
  NGi,
  NCard,
  NStatistic,
  NDataTable,
  NDivider,
  NText,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useDashboardStore } from '@/stores/dashboard'
import type { WatchlistItemWithPrice, AlertRecord } from '@/api'

const dashboard = useDashboardStore()

const priceColumns: DataTableColumns<WatchlistItemWithPrice> = [
  { title: '饰品名称', key: 'market_hash_name', ellipsis: { tooltip: true } },
  {
    title: '当前价格',
    key: 'latest_price',
    render(row) {
      if (row.latest_price == null) return '—'
      return `¥${row.latest_price.toFixed(2)}`
    },
  },
  { title: '平台', key: 'platform' },
  { title: '阈值(%)', key: 'threshold_percent' },
  {
    title: '状态',
    key: 'enabled',
    render(row) {
      return row.enabled ? '启用' : '禁用'
    },
  },
]

const alertColumns: DataTableColumns<AlertRecord> = [
  { title: '饰品', key: 'market_hash_name', ellipsis: { tooltip: true } },
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
  dashboard.loadAll()
})
</script>
