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
  const latestPriceCount = computed(() => summary.value?.latest_price_count ?? 0)
  const lastUpdate = computed(() => summary.value?.last_update ?? '-')

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
      const { data } = await api.alerts(1, 10)
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

  return {
    summary,
    watchlist,
    alerts,
    loading,
    error,
    activeWatchlistCount,
    extremeTrackCount,
    todayAlertCount,
    latestPriceCount,
    lastUpdate,
    fetchSummary,
    fetchWatchlist,
    fetchAlerts,
    loadAll,
  }
})
