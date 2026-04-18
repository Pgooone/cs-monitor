import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { type WatchlistItemWithPrice, type CreateWatchlistPayload, type UpdateWatchlistPayload } from '@/api'

export const useWatchlistStore = defineStore('watchlist', () => {
  const items = ref<WatchlistItemWithPrice[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchItems() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.watchlist()
      items.value = data
    } catch (e) {
      error.value = '获取监控清单失败'
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function addItem(payload: CreateWatchlistPayload) {
    const { data } = await api.createWatchlistItem(payload)
    await fetchItems()
    return data
  }

  async function updateItem(marketHashName: string, payload: UpdateWatchlistPayload) {
    const { data } = await api.updateWatchlistItem(marketHashName, payload)
    const idx = items.value.findIndex(i => i.market_hash_name === marketHashName)
    if (idx >= 0) {
      items.value[idx] = { ...items.value[idx], ...data, latest_price: items.value[idx].latest_price }
    }
    return data
  }

  async function removeItem(marketHashName: string) {
    await api.deleteWatchlistItem(marketHashName)
    items.value = items.value.filter(i => i.market_hash_name !== marketHashName)
  }

  async function toggleEnabled(item: WatchlistItemWithPrice) {
    const enabled = !item.enabled
    await updateItem(item.market_hash_name, { enabled })
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
  }
})
