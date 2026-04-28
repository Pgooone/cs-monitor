<template>
  <div class="dashboard">
    <!-- 骨架屏 -->
    <template v-if="dashboard.loading">
      <div class="dashboard__skeleton-header">
        <div class="cs-skeleton" style="width: 40%; height: 1.75rem;" />
        <div class="cs-skeleton" style="width: 30%; height: 1rem; margin-top: 0.5rem;" />
      </div>
      <div class="dashboard__grid-main">
        <div class="glass-card dashboard__hero-card">
          <div class="cs-skeleton" style="width: 50%; height: 0.75rem;" />
          <div class="cs-skeleton" style="width: 30%; height: 3rem; margin-top: 1rem;" />
          <div class="dashboard__bars">
            <div v-for="n in 12" :key="n" class="cs-skeleton" style="flex: 1; height: 100%;" />
          </div>
        </div>
        <div class="glass-card dashboard__actions-card">
          <div class="cs-skeleton" style="width: 40%; height: 0.75rem;" />
          <div v-for="n in 3" :key="n" class="cs-skeleton" style="width: 100%; height: 2.25rem; margin-top: 0.5rem;" />
          <div class="cs-skeleton" style="width: 60%; height: 1.5rem; margin-top: 1rem;" />
        </div>
      </div>
      <div class="dashboard__grid-stats">
        <div v-for="n in 3" :key="n" class="glass-card dashboard__stat-card">
          <div class="cs-skeleton" style="width: 50%; height: 0.75rem;" />
          <div class="cs-skeleton" style="width: 40%; height: 1.5rem; margin-top: 0.75rem;" />
        </div>
      </div>
    </template>

    <!-- 真实内容 -->
    <template v-else>
      <!-- 1. 顶部标题区 -->
      <div class="dashboard__header">
        <div class="dashboard__header-left">
          <h2 class="dashboard__title">终端概览</h2>
          <p class="dashboard__desc">实时监控 SteamDT API 饰品价格波动与趋势。</p>
        </div>
        <div class="dashboard__api-status">
          <div class="dashboard__api-dot-wrap">
            <div class="dashboard__api-dot" />
            <span class="dashboard__api-label">API 生命周期</span>
          </div>
          <span class="dashboard__api-value">活跃 ({{ formatUTCToLocal(dashboard.lastUpdate) }})</span>
        </div>
      </div>

      <!-- 2. 主区域 2:1 -->
      <div class="dashboard__grid-main">
        <!-- 左大卡片 -->
        <div class="glass-card dashboard__hero-card">
          <div class="dashboard__hero-glow" />
          <div class="dashboard__hero-content">
            <span class="dashboard__hero-label">监控饰品总数量</span>
            <div class="dashboard__hero-value-wrap">
              <span class="dashboard__hero-value">{{ dashboard.activeWatchlistCount }}</span>
              <span class="dashboard__hero-extreme">极致追踪: {{ dashboard.extremeTrackCount }}</span>
            </div>
          </div>
          <div class="dashboard__bars">
            <div
              v-for="(h, i) in barHeights"
              :key="i"
              class="dashboard__bar"
              :style="{ height: animatedBars[i] ? `${h}%` : '0%', transitionDelay: `${i * 50}ms` }"
            />
          </div>
        </div>

        <!-- 右卡片 -->
        <div class="glass-card dashboard__actions-card">
          <div class="dashboard__actions-header">
            <span class="dashboard__actions-label">核心功能</span>
            <Zap class="w-4 h-4 text-brand" />
          </div>
          <div class="dashboard__actions-list">
            <button class="btn-outline w-full justify-start text-xs py-2 h-9 px-3" @click="$router.push({ name: 'ExtremeTrack' })">
              <LayoutGrid class="w-3 h-3" />
              极致追踪配置
            </button>
            <button class="btn-outline w-full justify-start text-xs py-2 h-9 px-3" @click="handleRefresh">
              <RefreshCw class="w-3 h-3" />
              全量刷新数据
            </button>
            <button class="btn-outline w-full justify-start text-xs py-2 h-9 px-3">
              <Terminal class="w-3 h-3" />
              查看运行日志
            </button>
          </div>
          <div class="dashboard__actions-footer">
            <span class="dashboard__actions-alert-label">今日警报活跃</span>
            <div class="dashboard__actions-alert-value">
              <Bell class="w-5 h-5 text-rise mr-2" />
              <span>{{ dashboard.todayAlertCount }} 起警报</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 底部统计卡片 -->
      <div class="dashboard__grid-stats">
        <div class="glass-card dashboard__stat-card">
          <span class="dashboard__stat-label">总价格记录数</span>
          <span class="dashboard__stat-value">{{ (dashboard.summary?.latest_price_count || 0).toLocaleString() }}</span>
        </div>
        <div class="glass-card dashboard__stat-card">
          <div class="dashboard__stat-header">
            <span class="dashboard__stat-label">今日采集次数</span>
            <span class="dashboard__stat-badge">活跃中</span>
          </div>
          <span class="dashboard__stat-value">{{ (dashboard.todayCollectionCount || 0).toLocaleString() }}</span>
        </div>
        <div class="glass-card dashboard__stat-card">
          <span class="dashboard__stat-label">昨日告警数</span>
          <span class="dashboard__stat-value">{{ dashboard.summary?.yesterday_alert_count || 0 }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Zap, LayoutGrid, RefreshCw, Terminal, Bell } from 'lucide-vue-next'
import { useDashboardStore } from '@/stores/dashboard'
import { toastSuccess } from '@/composables/useToast'
import { formatUTCToLocal } from '@/utils/date'

const dashboard = useDashboardStore()

// 柱状图高度（伪数据，12 根柱子）
const barHeights = [30, 50, 40, 60, 45, 70, 65, 80, 75, 95, 85, 100]
const animatedBars = ref<boolean[]>(new Array(12).fill(false))

onMounted(() => {
  dashboard.loadAll()
  // 延迟触发动画
  setTimeout(() => {
    animatedBars.value = new Array(12).fill(true)
  }, 100)
})

function handleRefresh() {
  dashboard.loadAll()
  toastSuccess('全量刷新已触发')
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 80rem;
  margin: 0 auto;
}

/* ===== 顶部标题区 ===== */
.dashboard__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.dashboard__title {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin: 0;
}

.dashboard__desc {
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
}

.dashboard__api-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(15, 15, 18, 0.5);
  border: 1px solid #1f1f23;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
}

.dashboard__api-dot-wrap {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.dashboard__api-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6366f1;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.dashboard__api-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #94a3b8;
}

.dashboard__api-value {
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #6366f1;
}

/* ===== 主区域 Grid ===== */
.dashboard__grid-main {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .dashboard__grid-main {
    grid-template-columns: 2fr 1fr;
  }
}

/* ===== 左大卡片 ===== */
.dashboard__hero-card {
  position: relative;
  height: 16rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
}

.dashboard__hero-glow {
  position: absolute;
  top: -20%;
  right: -5%;
  width: 16rem;
  height: 16rem;
  background: rgba(99, 102, 241, 0.1);
  filter: blur(80px);
  border-radius: 50%;
  transition: background 500ms;
  pointer-events: none;
}

.dashboard__hero-card:hover .dashboard__hero-glow {
  background: rgba(99, 102, 241, 0.2);
}

.dashboard__hero-content {
  position: relative;
  z-index: 1;
}

.dashboard__hero-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.dashboard__hero-value-wrap {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.dashboard__hero-value {
  font-size: 3rem;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  color: #ffffff;
}

.dashboard__hero-extreme {
  font-size: 0.875rem;
  font-weight: 700;
  color: #22c55e;
  margin-bottom: 0.5rem;
}

/* ===== 柱状图 ===== */
.dashboard__bars {
  display: flex;
  align-items: flex-end;
  gap: 0.25rem;
  height: 6rem;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.dashboard__bar {
  flex: 1;
  background: rgba(99, 102, 241, 0.2);
  border-radius: 2px 2px 0 0;
  transition: height 800ms ease-out;
  cursor: pointer;
}

.dashboard__bar:hover {
  background: #6366f1;
}

/* ===== 右卡片 ===== */
.dashboard__actions-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.dashboard__actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.dashboard__actions-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.dashboard__actions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dashboard__actions-footer {
  padding-top: 1rem;
  border-top: 1px solid #1f1f23;
  margin-top: 1rem;
}

.dashboard__actions-alert-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 0.75rem;
  display: block;
}

.dashboard__actions-alert-value {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: #ffffff;
}

/* ===== 底部统计卡片 ===== */
.dashboard__grid-stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .dashboard__grid-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}

.dashboard__stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dashboard__stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard__stat-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.dashboard__stat-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.dashboard__stat-value {
  font-size: 1.5rem;
  font-weight: 900;
  color: #ffffff;
  font-variant-numeric: tabular-nums;
}

/* ===== 骨架屏 ===== */
.dashboard__skeleton-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

/* ===== 浅色模式覆盖 ===== */
html:not(.dark) .dashboard__title { color: #0f172a; }
html:not(.dark) .dashboard__desc { color: #64748b; }
html:not(.dark) .dashboard__api-status {
  background: rgba(255, 255, 255, 0.8);
  border-color: #e2e8f0;
}
html:not(.dark) .dashboard__hero-value { color: #0f172a; }
html:not(.dark) .dashboard__stat-value { color: #0f172a; }
html:not(.dark) .dashboard__actions-footer { border-color: #e2e8f0; }
html:not(.dark) .dashboard__actions-alert-value { color: #0f172a; }
</style>
