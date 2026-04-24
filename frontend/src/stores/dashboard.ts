import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { type DashboardSummary, type WatchlistItemWithPrice, type AlertRecord } from '@/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const summary = ref<DashboardSummary | null>(null)
  const watchlist = ref<WatchlistItemWithPrice[]>([])
  const alerts = ref<AlertRecord[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activeWatchlistCount = computed(() => summary.value?.active_watchlist ?? 0)
  const extremeTrackCount = computed(() => summary.value?.extreme_track_count ?? 0)
  const todayAlertCount = computed(() => summary.value?.today_alert_count ?? 0)
  const yesterdayAlertCount = computed(() => summary.value?.yesterday_alert_count ?? 0)
  const latestPriceCount = computed(() => summary.value?.latest_price_count ?? 0)
  const lastUpdate = computed(() => summary.value?.last_update ?? '-')
  const todayCollectionCount = computed(() => summary.value?.today_collection_count ?? 0)
  const checkIntervalMinutes = computed(() => summary.value?.check_interval_minutes ?? 30)
  const portfolioHistory = computed(() => summary.value?.portfolio_history ?? [])
  const topVolatile = computed(() => summary.value?.top_volatile ?? [])
  const apiQuotaPercent = computed(() => summary.value?.api_quota_percent ?? 0)
  const watchlistSparkline = computed(() => summary.value?.watchlist_sparkline ?? [])

  const alertDiff = computed(() => {
    const today = todayAlertCount.value
    const yesterday = yesterdayAlertCount.value
    return {
      diff: today - yesterday,
      percent: yesterday > 0 ? Math.round(((today - yesterday) / yesterday) * 100) : (today > 0 ? 100 : 0),
      up: today >= yesterday,
    }
  })

  async function fetchSummary() {
    try {
      const { data } = await api.dashboardSummary()
      summary.value = data
    } catch (e) {
      error.value = '获取概览数据失败'
      console.error(e)
    }
  }

  async function fetchWatchlist() {
    try {
      const { data } = await api.watchlist()
      watchlist.value = data
    } catch (e) {
      error.value = '获取监控清单失败'
      console.error(e)
    }
  }

  async function fetchAlerts() {
    try {
      const { data } = await api.alerts(1, 20)
      alerts.value = data.items
    } catch (e) {
      error.value = '获取告警记录失败'
      console.error(e)
    }
  }

  async function loadAll() {
    loading.value = true
    error.value = null
    await Promise.all([fetchSummary(), fetchWatchlist(), fetchAlerts()])
    loading.value = false
  }

  function incrementTodayAlertCount() {
    if (summary.value) {
      summary.value.today_alert_count++
    }
  }

  return {
    summary,
    watchlist,
    alerts,
    loading,
    error,
    activeWatchlistCount,
    extremeTrackCount,
    todayAlertCount,
    yesterdayAlertCount,
    latestPriceCount,
    lastUpdate,
    todayCollectionCount,
    checkIntervalMinutes,
    portfolioHistory,
    topVolatile,
    apiQuotaPercent,
    watchlistSparkline,
    alertDiff,
    fetchSummary,
    fetchWatchlist,
    fetchAlerts,
    loadAll,
    incrementTodayAlertCount,
  }
})
