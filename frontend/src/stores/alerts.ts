import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { type AlertRecord, type AlertStatsResponse } from '@/api'

export const useAlertsStore = defineStore('alerts', () => {
  const items = ref<AlertRecord[]>([])
  const total = ref(0)
  const page = ref(1)
  const limit = ref(20)
  const stats = ref<AlertStatsResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAlerts(filters?: {
    alert_type?: string
    start_date?: string
    end_date?: string
    market_hash_name?: string
  }) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.alerts(page.value, limit.value, filters)
      items.value = data.items
      total.value = data.total
    } catch (e) {
      error.value = '获取告警记录失败'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchStats(filters?: {
    start_date?: string
    end_date?: string
  }) {
    try {
      const { data } = await api.alertStats(filters)
      stats.value = data
    } catch (e) {
      console.error(e)
    }
  }

  function setPage(p: number) {
    page.value = p
  }

  return {
    items,
    total,
    page,
    limit,
    stats,
    loading,
    error,
    fetchAlerts,
    fetchStats,
    setPage,
  }
})
