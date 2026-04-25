<template>
  <div class="dashboard">
    <!-- 骨架屏 -->
    <template v-if="dashboard.loading">
      <div class="dashboard__skeleton-header">
        <div class="skeleton-line skeleton-line--title" style="width: 40%; height: 1.75rem;" />
        <div class="skeleton-line" style="width: 30%; height: 1rem; margin-top: 0.5rem;" />
      </div>
      <n-grid :x-gap="16" :y-gap="16" cols="1 640:2 1024:4">
        <n-gi v-for="n in 4" :key="n">
          <div class="skeleton-kpi">
            <div class="skeleton-line" style="width: 60%; height: 1rem;" />
            <div class="skeleton-line" style="width: 40%; height: 2.5rem; margin-top: 1rem;" />
          </div>
        </n-gi>
      </n-grid>
      <n-grid :x-gap="16" :y-gap="16" cols="1 1024:3" class="dashboard__main">
        <n-gi :span="2">
          <SkeletonChart />
        </n-gi>
        <n-gi>
          <div class="skeleton-feed">
            <div class="skeleton-line" style="width: 40%; height: 1rem; margin-bottom: 1rem;" />
            <div v-for="n in 5" :key="n" class="skeleton-line" style="width: 100%; height: 2.5rem; margin-bottom: 0.5rem;" />
          </div>
        </n-gi>
      </n-grid>
    </template>

    <!-- 真实内容 -->
    <template v-else>
      <!-- 欢迎语 + 状态栏 -->
      <div class="dashboard__welcome">
        <h1 class="dashboard__greeting">{{ greeting }}，{{ t('dashboard.greeting') }}</h1>
        <div class="dashboard__status-bar">
          <span class="dashboard__status-item">
            <span class="dashboard__status-icon">🔄</span>
            {{ t('dashboard.todayCollections') }} <strong class="font-mono-num">{{ dashboard.todayCollectionCount }}</strong> {{ t('dashboard.times') }}
          </span>
          <span class="dashboard__status-item">
            <span class="dashboard__status-icon">🔔</span>
            {{ t('dashboard.todayAlerts') }} <strong class="font-mono-num">{{ dashboard.todayAlertCount }}</strong> {{ t('dashboard.items') }}
          </span>
          <span class="dashboard__status-item">
            <span class="dashboard__status-icon">🕐</span>
            {{ t('dashboard.lastUpdate') }} {{ formattedLastUpdate }}
          </span>
        </div>
      </div>

      <!-- 4 张 KPI 卡 -->
      <n-grid :x-gap="16" :y-gap="16" cols="1 640:2 1024:4">
        <!-- 监控饰品数 -->
        <n-gi>
          <KpiCard
            title="监控饰品"
            :value="dashboard.activeWatchlistCount"
            icon="📋"
            :icon-color="brand[500]"
            :icon-bg="`${brand[500]}1F`"
            variant="default"
            glass
          >
            <template #extra>
              <MiniSparkline
                :data="sparklineData"
                :color="brand[500]"
                :width="120"
                :height="36"
              />
            </template>
          </KpiCard>
        </n-gi>

        <!-- 今日告警 -->
        <n-gi>
          <KpiCard
            title="今日告警"
            :value="dashboard.todayAlertCount"
            icon="🔔"
            :icon-color="semantic.error.light"
            :icon-bg="`${semantic.error.light}1F`"
            variant="default"
            glass
          >
            <template #extra>
              <div class="kpi-compare">
                <span
                  class="kpi-compare__badge"
                  :class="dashboard.alertDiff.up ? 'kpi-compare__badge--up' : 'kpi-compare__badge--down'"
                >
                  {{ dashboard.alertDiff.up ? '▲' : '▼' }} {{ Math.abs(dashboard.alertDiff.percent) }}%
                </span>
                <span class="kpi-compare__label">较昨日</span>
              </div>
            </template>
          </KpiCard>
        </n-gi>

        <!-- 极致追踪 -->
        <n-gi>
          <KpiCard
            title="极致追踪"
            :value="dashboard.extremeTrackCount"
            icon="🎯"
            :icon-color="semantic.success.light"
            :icon-bg="`${semantic.success.light}1F`"
            variant="default"
            glass
          >
            <template #extra>
              <div class="kpi-status">
                <span
                  class="kpi-status__dot"
                  :class="{ 'kpi-status__dot--active': dashboard.extremeTrackCount > 0 }"
                />
                <span class="kpi-status__text">
                  {{ dashboard.extremeTrackCount > 0 ? '运行中' : '未启用' }}
                </span>
              </div>
            </template>
          </KpiCard>
        </n-gi>

        <!-- API 配额 -->
        <n-gi>
          <KpiCard
            title="API 配额"
            :value="`${Math.round(dashboard.apiQuotaPercent)}%`"
            icon="⚡"
            :icon-color="semantic.warning.light"
            :icon-bg="`${semantic.warning.light}1F`"
            variant="default"
            glass
          >
            <template #extra>
              <div class="ring-progress">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <circle
                    cx="20" cy="20" r="16"
                    fill="none"
                    stroke="rgba(0,0,0,0.08)"
                    stroke-width="3"
                  />
                  <circle
                    cx="20" cy="20" r="16"
                    fill="none"
                    :stroke="quotaColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    :stroke-dasharray="`${quotaArc} 100.5`"
                    transform="rotate(-90 20 20)"
                    style="transition: stroke-dasharray 600ms ease;"
                  />
                </svg>
              </div>
            </template>
          </KpiCard>
        </n-gi>
      </n-grid>

      <!-- 主图区：组合价值曲线 + 今日告警流 -->
      <n-grid :x-gap="16" :y-gap="16" cols="1 1024:3" class="dashboard__main">
        <n-gi :span="2">
          <n-card
            title="组合价值趋势（30天）"
            class="dashboard__chart-card"
            :bordered="false"
            size="small"
          >
            <PortfolioChart
              :data="dashboard.portfolioHistory"
              :is-dark="isDark"
            />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card
            class="dashboard__feed-card"
            :bordered="false"
            size="small"
          >
            <template #header>
              <div class="feed-card-header">
                <span class="feed-card-header__title">今日告警流</span>
                <n-badge :value="dashboard.alerts.length" :max="99" />
              </div>
            </template>
            <AlertFeed :alerts="dashboard.alerts" />
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 热度榜 -->
      <n-card
        title="24h 波动热度榜"
        class="dashboard__heatmap"
        :bordered="false"
        size="small"
      >
        <div class="heatmap-grid">
          <div
            v-for="item in dashboard.topVolatile"
            :key="item.market_hash_name"
            class="heatmap-item"
          >
            <div class="heatmap-item__info">
              <div class="heatmap-item__name">{{ item.market_hash_name }}</div>
              <div class="heatmap-item__price font-mono-num">
                <AnimatedNumber
                  v-if="item.current_price != null"
                  :value="item.current_price"
                  :precision="2"
                  prefix="¥"
                />
                <span v-else>—</span>
              </div>
            </div>
            <div class="heatmap-item__chart">
              <MiniSparkline
                v-if="item.sparkline.length >= 2"
                :data="item.sparkline"
                :color="item.change_percent >= 0 ? colorUp : colorDown"
                :width="80"
                :height="28"
              />
              <div
                v-else
                class="heatmap-item__bar"
                :class="item.change_percent >= 0 ? 'heatmap-item__bar--up' : 'heatmap-item__bar--down'"
                :style="{ width: `${Math.min(100, Math.abs(item.change_percent) * 3)}%` }"
              />
            </div>
            <div
              class="heatmap-item__change font-mono-num"
              :class="item.change_percent >= 0 ? 'heatmap-item__change--up' : 'heatmap-item__change--down'"
            >
              {{ item.change_percent >= 0 ? '+' : '' }}{{ item.change_percent.toFixed(2) }}%
            </div>
          </div>
        </div>
      </n-card>

      <!-- 采集状态 -->
      <CollectionStatus
        :last-update="dashboard.lastUpdate"
        :check-interval-minutes="dashboard.checkIntervalMinutes"
        :today-collection-count="dashboard.todayCollectionCount"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { NGrid, NGi, NCard, NBadge } from 'naive-ui'
import { useDashboardStore } from '@/stores/dashboard'
import { useWebsocketStore } from '@/stores/websocket'
import { useTheme } from '@/composables/useTheme'
import { brand, semantic } from '@/styles/tokens'
import KpiCard from '@/components/business/KpiCard.vue'
import MiniSparkline from '@/components/business/MiniSparkline.vue'
import PortfolioChart from '@/components/business/PortfolioChart.vue'
import AlertFeed from '@/components/business/AlertFeed.vue'
import CollectionStatus from '@/components/business/CollectionStatus.vue'
import SkeletonChart from '@/components/base/SkeletonChart.vue'
import AnimatedNumber from '@/components/base/AnimatedNumber.vue'

const dashboard = useDashboardStore()
const wsStore = useWebsocketStore()
const { isDark, colorUp, colorDown } = useTheme()
const { t } = useI18n()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return t('dashboard.night')
  if (hour < 12) return t('dashboard.morning')
  if (hour < 18) return t('dashboard.afternoon')
  return t('dashboard.evening')
})

const formattedLastUpdate = computed(() => {
  const t = dashboard.lastUpdate
  if (!t || t === '-') return '—'
  try {
    const d = new Date(t)
    return d.toLocaleString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return t
  }
})

const sparklineData = computed(() => {
  const data = dashboard.watchlistSparkline
  return data.length >= 2 ? data : [0, 0]
})

const quotaColor = computed(() => {
  const p = dashboard.apiQuotaPercent
  if (p < 50) return semantic.success.light
  if (p < 80) return semantic.warning.light
  return semantic.error.light
})

const quotaArc = computed(() => {
  const p = Math.min(100, Math.max(0, dashboard.apiQuotaPercent))
  return (p / 100) * 100.5
})

// WebSocket 告警推送
function handleWsAlert(data: any) {
  if (data?.type === 'alert' && data.data) {
    const alert = data.data
    dashboard.alerts.unshift({
      id: Date.now(),
      market_hash_name: alert.market_hash_name,
      alert_type: alert.alert_type,
      current_price: alert.current_price,
      baseline_price: alert.baseline_price,
      change_percent: alert.change_percent,
      notified_at: alert.timestamp || new Date().toISOString(),
    })
    dashboard.incrementTodayAlertCount()
  }
}

onMounted(() => {
  dashboard.loadAll()
  wsStore.connectAlerts(handleWsAlert)
})

onUnmounted(() => {
  wsStore.disconnectAlerts()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feed-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.feed-card-header__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--cs-text-primary);
}

/* ===== 欢迎语区域 ===== */
.dashboard__welcome {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.25rem 0;
}
.dashboard__greeting {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  color: var(--cs-text-primary);
  letter-spacing: -0.02em;
  line-height: 1.3;
}
.dashboard__status-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.dashboard__status-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: var(--cs-text-secondary);
  transition: color var(--cs-transition-fast);
}
.dashboard__status-item strong {
  color: var(--cs-text-primary);
  font-weight: 600;
}
.dashboard__status-icon {
  font-size: 0.875rem;
  opacity: 0.85;
}

/* ===== KPI 对比 ===== */
.kpi-compare {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.kpi-compare__badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-family: 'JetBrains Mono', monospace;
  transition: all var(--cs-transition-fast);
}
.kpi-compare__badge--up {
  background: v-bind('colorUp') + '22';
  color: v-bind('colorUp');
}
.kpi-compare__badge--down {
  background: v-bind('colorDown') + '22';
  color: v-bind('colorDown');
}
.kpi-compare__label {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
}

/* ===== KPI 状态 ===== */
.kpi-status {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}
.kpi-status__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cs-text-muted);
  transition: background var(--cs-transition-fast);
}
.kpi-status__dot--active {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25); }
  50% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.1); }
}
.kpi-status__text {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
}

/* ===== 环形进度 ===== */
.ring-progress {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

/* ===== 主图区 ===== */
.dashboard__main {
  margin-top: 0.25rem;
}
.dashboard__chart-card,
.dashboard__feed-card,
.dashboard__heatmap {
  border-radius: 1rem;
  background: var(--cs-bg-card);
  border: 1px solid var(--cs-border-light);
  overflow: hidden;
  box-shadow: var(--cs-shadow-sm);
  transition: box-shadow var(--cs-transition-base);
}
.dashboard__chart-card:hover,
.dashboard__feed-card:hover,
.dashboard__heatmap:hover {
  box-shadow: var(--cs-shadow-md);
}

/* ===== 热度榜 ===== */
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.875rem;
}
.heatmap-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1rem 1.125rem;
  border-radius: 0.875rem;
  background: var(--cs-bg-card);
  border: 1px solid var(--cs-border-light);
  transition: transform var(--cs-transition-base), box-shadow var(--cs-transition-base);
}
.heatmap-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--cs-shadow-md);
}
.heatmap-item__info {
  flex: 1;
  min-width: 0;
}
.heatmap-item__name {
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.25rem;
  color: var(--cs-text-primary);
}
.heatmap-item__price {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--cs-text-secondary);
}
.heatmap-item__chart {
  width: 80px;
  flex-shrink: 0;
}
.heatmap-item__bar {
  height: 4px;
  border-radius: 2px;
  background: currentColor;
  transition: width 600ms ease;
}
.heatmap-item__bar--up {
  background: v-bind('colorUp');
}
.heatmap-item__bar--down {
  background: v-bind('colorDown');
}
.heatmap-item__change {
  font-size: 0.875rem;
  font-weight: 700;
  width: 72px;
  text-align: right;
  flex-shrink: 0;
}
.heatmap-item__change--up {
  color: v-bind('colorUp');
}
.heatmap-item__change--down {
  color: v-bind('colorDown');
}

/* ===== 骨架屏 ===== */
.dashboard__skeleton-header {
  margin-bottom: 0.5rem;
}
.skeleton-kpi {
  border-radius: 1rem;
  padding: 1.25rem;
  background: var(--cs-bg-card);
  border: 1px solid var(--cs-border-light);
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
.skeleton-feed {
  border-radius: 1rem;
  padding: 1rem;
  background: var(--cs-bg-card);
  border: 1px solid var(--cs-border-light);
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
