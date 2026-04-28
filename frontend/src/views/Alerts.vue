<template>
  <div class="alerts">
    <!-- 标题区 -->
    <div class="alerts__header">
      <div>
        <h2 class="alerts__title">历史告警记录</h2>
        <p class="alerts__desc">查看系统根据预设条件触发的实时推送历史。</p>
      </div>
    </div>

    <!-- 骨架屏 -->
    <div v-if="loading" class="glass-card alerts__table-wrap">
      <div v-for="n in 5" :key="n" class="alerts__skeleton-row">
        <div class="skeleton-line" style="width: 20%; height: 1rem;" />
        <div class="skeleton-line" style="width: 25%; height: 1rem;" />
        <div class="skeleton-line" style="width: 35%; height: 1rem;" />
        <div class="skeleton-line" style="width: 15%; height: 1rem;" />
      </div>
    </div>

    <!-- 空态 -->
    <div v-else-if="items.length === 0" class="glass-card alerts__empty">
      <Bell class="alerts__empty-icon" />
      <p class="alerts__empty-text">暂无告警记录</p>
    </div>

    <!-- 表格 -->
    <div v-else class="glass-card alerts__table-wrap">
      <table class="alerts__table">
        <thead>
          <tr>
            <th>触发时间</th>
            <th>饰品名称</th>
            <th>警报详情</th>
            <th>类型</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="alert in items" :key="alert.id">
            <td class="alerts__time font-mono-num">{{ formatDateTime(alert.notified_at) }}</td>
            <td class="alerts__name">{{ alert.display_name || alert.market_hash_name }}</td>
            <td class="alerts__detail">
              当前价格: ¥{{ getAlertPrice(alert)?.toFixed(2) || '—' }}
              <span
                v-if="getAlertChangePercent(alert) != null"
                :class="getAlertChangePercent(alert)! >= 0 ? 'alerts__change--up' : 'alerts__change--down'"
              >
                ({{ getAlertChangePercent(alert)! >= 0 ? '+' : '' }}{{ getAlertChangePercent(alert)!.toFixed(2) }}%变动)
              </span>
            </td>
            <td>
              <span class="alerts__type-badge" :class="getTypeBadgeClass(alert.alert_type)">
                <component :is="getTypeIcon(alert.alert_type)" class="w-3 h-3" />
                {{ typeMap[alert.alert_type] || alert.alert_type }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div v-if="total > limit" class="alerts__pagination">
      <n-pagination
        v-model:page="page"
        :page-count="Math.ceil(total / limit)"
        :page-size="limit"
        @update:page="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NPagination } from 'naive-ui'
import { Bell, TrendingDown, TrendingUp, AlertCircle, Zap } from 'lucide-vue-next'
import api, { type AlertRecord } from '@/api'
import { toastError } from '@/composables/useToast'

const items = ref<AlertRecord[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)
const loading = ref(false)

const typeMap: Record<string, string> = {
  price_surge: '价格暴涨',
  price_drop: '价格暴跌',
  price_change: '价格变动',
  quantity_change: '数量变动',
  both: '综合变动',
}

function getAlertPrice(alert: AlertRecord): number | null {
  if ('current_price' in alert) return (alert as any).current_price
  if ('curr_price' in alert) return (alert as any).curr_price
  return null
}

function getAlertChangePercent(alert: AlertRecord): number | null {
  if ('change_percent' in alert) return (alert as any).change_percent
  if ('price_change_percent' in alert) return (alert as any).price_change_percent
  return null
}

function getTypeIcon(type: string) {
  if (type === 'price_drop') return TrendingDown
  if (type === 'price_surge') return TrendingUp
  if (type === 'quantity_change') return AlertCircle
  return Zap
}

function getTypeBadgeClass(type: string): string {
  if (type === 'price_drop') return 'alerts__type-badge--drop'
  if (type === 'price_surge') return 'alerts__type-badge--surge'
  if (type === 'quantity_change') return 'alerts__type-badge--volume'
  return 'alerts__type-badge--default'
}

function formatDateTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchData() {
  loading.value = true
  try {
    const { data } = await api.alerts(page.value, limit.value)
    items.value = data.items
    total.value = data.total
  } catch (e) {
    toastError('获取告警记录失败')
  } finally {
    loading.value = false
  }
}

function handlePageChange(p: number) {
  page.value = p
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.alerts {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 80rem;
  margin: 0 auto;
}

.alerts__title {
  font-size: 1.75rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin: 0;
}

.alerts__desc {
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
}

/* 表格容器 */
.alerts__table-wrap {
  padding: 0;
  overflow: hidden;
}

.alerts__table {
  width: 100%;
  text-align: left;
  border-collapse: collapse;
}

.alerts__table thead {
  background: rgba(15, 15, 18, 0.5);
  border-bottom: 1px solid #1f1f23;
}

.alerts__table th {
  padding: 1rem 1.5rem;
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}

.alerts__table td {
  padding: 1rem 1.5rem;
  font-size: 0.875rem;
}

.alerts__table tbody tr {
  transition: background 200ms;
}

.alerts__table tbody tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.alerts__table tbody tr + tr {
  border-top: 1px solid #1f1f23;
}

.alerts__time {
  color: #94a3b8;
  font-size: 0.75rem;
}

.alerts__name {
  font-weight: 700;
  color: #6366f1;
  font-size: 0.875rem;
}

.alerts__detail {
  font-size: 0.875rem;
  font-weight: 500;
  color: #ffffff;
}

.alerts__change--up {
  color: #ef4444;
}

.alerts__change--down {
  color: #22c55e;
}

/* 类型标签 */
.alerts__type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 10px;
  font-weight: 700;
  border: 1px solid transparent;
}

.alerts__type-badge--drop {
  border-color: rgba(34, 197, 94, 0.3);
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}

.alerts__type-badge--surge {
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.alerts__type-badge--volume {
  border-color: rgba(245, 158, 11, 0.3);
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.alerts__type-badge--default {
  border-color: rgba(99, 102, 241, 0.2);
  color: #6366f1;
  background: rgba(99, 102, 241, 0.05);
}

/* 空态 */
.alerts__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
}

.alerts__empty-icon {
  width: 3rem;
  height: 3rem;
  color: #94a3b8;
  opacity: 0.3;
  margin-bottom: 1rem;
}

.alerts__empty-text {
  font-size: 0.875rem;
  color: #94a3b8;
  font-weight: 500;
}

/* 骨架屏 */
.alerts__skeleton-row {
  display: flex;
  gap: 2rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #1f1f23;
}

.skeleton-line {
  border-radius: 0.25rem;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.04) 25%, rgba(255, 255, 255, 0.08) 50%, rgba(255, 255, 255, 0.04) 75%);
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 分页 */
.alerts__pagination {
  display: flex;
  justify-content: center;
}

/* 浅色模式 */
html:not(.dark) .alerts__title { color: #0f172a; }
html:not(.dark) .alerts__desc { color: #64748b; }
html:not(.dark) .alerts__table thead { background: rgba(248, 250, 252, 0.5); border-color: #e2e8f0; }
html:not(.dark) .alerts__table tbody tr:hover { background: rgba(0, 0, 0, 0.02); }
html:not(.dark) .alerts__table tbody tr + tr { border-color: #e2e8f0; }
html:not(.dark) .alerts__detail { color: #0f172a; }
html:not(.dark) .alerts__name { color: #6366f1; }
html:not(.dark) .alerts__type-badge--drop { border-color: rgba(34, 197, 94, 0.3); color: #16a34a; background: rgba(34, 197, 94, 0.08); }
html:not(.dark) .alerts__type-badge--surge { border-color: rgba(239, 68, 68, 0.3); color: #dc2626; background: rgba(239, 68, 68, 0.08); }
html:not(.dark) .alerts__type-badge--volume { border-color: rgba(245, 158, 11, 0.3); color: #d97706; background: rgba(245, 158, 11, 0.08); }
html:not(.dark) .alerts__type-badge--default { border-color: rgba(99, 102, 241, 0.2); color: #4f46e5; background: rgba(99, 102, 241, 0.05); }
html:not(.dark) .alerts__skeleton-row { border-color: #e2e8f0; }
html:not(.dark) .skeleton-line { background: linear-gradient(90deg, rgba(0, 0, 0, 0.04) 25%, rgba(0, 0, 0, 0.08) 50%, rgba(0, 0, 0, 0.04) 75%); background-size: 200% 100%; }
</style>
