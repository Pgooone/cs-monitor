import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { type ExtremeTrackConfig, type CreateExtremeTrackPayload, type UpdateExtremeTrackPayload } from '@/api'

export const useExtremeTrackStore = defineStore('extremeTrack', () => {
  const items = ref<ExtremeTrackConfig[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchItems() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.extremeTrackList()
      items.value = data
    } catch (e) {
      error.value = '获取极致追踪列表失败'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function addItem(payload: CreateExtremeTrackPayload) {
    const { data } = await api.createExtremeTrack(payload)
    await fetchItems()
    return data
  }

  async function updateItem(marketHashName: string, platform: string, payload: UpdateExtremeTrackPayload) {
    const { data } = await api.updateExtremeTrack(marketHashName, platform, payload)
    const idx = items.value.findIndex(
      i => i.market_hash_name === marketHashName && i.platform === platform,
    )
    if (idx >= 0) {
      items.value[idx] = { ...items.value[idx], ...data }
    }
    return data
  }

  async function removeItem(marketHashName: string, platform: string) {
    await api.deleteExtremeTrack(marketHashName, platform)
    items.value = items.value.filter(
      i => !(i.market_hash_name === marketHashName && i.platform === platform),
    )
  }

  async function toggleEnabled(item: ExtremeTrackConfig) {
    const enabled = !item.enabled
    await updateItem(item.market_hash_name, item.platform, { enabled })
  }

  function updateRealtimeData(trackId: string, data: any) {
    const [marketHashName, platform] = trackId.split('@')
    const idx = items.value.findIndex(
      i => i.market_hash_name === marketHashName && i.platform === platform,
    )
    if (idx >= 0) {
      // 附加实时数据到项上（通过 Vue 响应式）
      const item = items.value[idx] as any
      if (!item._realtime) item._realtime = []
      item._realtime.unshift({
        alert_type: data.alert_type,
        curr_price: data.curr_price,
        prev_price: data.prev_price,
        curr_quantity: data.curr_quantity,
        prev_quantity: data.prev_quantity,
        timestamp: data.timestamp || new Date().toISOString(),
      })
      if (item._realtime.length > 20) item._realtime.pop()
    }
  }

  return {
    items,
    loading,
    error,
    fetchItems,
    addItem,
    updateItem,
    removeItem,
    toggleEnabled,
    updateRealtimeData,
  }
})
