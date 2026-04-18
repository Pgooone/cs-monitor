import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface DashboardSummary {
  active_watchlist: number
  extreme_track_count: number
  today_alert_count: number
  latest_price_count: number
  last_update: string | null
}

export interface WatchlistItem {
  id: number
  market_hash_name: string
  display_name: string | null
  threshold_percent: number
  enabled: number
  created_at: string | null
  updated_at: string | null
}

export interface WatchlistItemWithPrice {
  id: number
  market_hash_name: string
  display_name: string | null
  threshold_percent: number
  enabled: number
  latest_price: number | null
  platform: string | null
  price_updated_at: string | null
  created_at: string | null
  updated_at: string | null
}

export interface AlertRecord {
  id: number
  market_hash_name: string
  alert_type: string
  current_price: number | null
  baseline_price: number | null
  change_percent: number | null
  notified_at: string
}

export interface AlertListResponse {
  items: AlertRecord[]
  total: number
  page: number
  limit: number
}

export interface PriceHistoryItem {
  id: number
  market_hash_name: string
  platform: string
  price: number
  recorded_at: string
}

export interface PlatformPriceItem {
  market_hash_name: string
  platform: string
  price: number
  recorded_at: string
}

export interface CreateWatchlistPayload {
  market_hash_name: string
  display_name?: string | null
  threshold_percent?: number
  enabled?: boolean
}

export interface UpdateWatchlistPayload {
  display_name?: string | null
  threshold_percent?: number
  enabled?: boolean
}

export default {
  health() {
    return api.get('/health')
  },
  dashboardSummary() {
    return api.get<DashboardSummary>('/dashboard/summary')
  },
  watchlist() {
    return api.get<WatchlistItemWithPrice[]>('/watchlist')
  },
  createWatchlistItem(payload: CreateWatchlistPayload) {
    return api.post<WatchlistItem>('/watchlist', payload)
  },
  updateWatchlistItem(marketHashName: string, payload: UpdateWatchlistPayload) {
    return api.put<WatchlistItem>(`/watchlist/${encodeURIComponent(marketHashName)}`, payload)
  },
  deleteWatchlistItem(marketHashName: string) {
    return api.delete(`/watchlist/${encodeURIComponent(marketHashName)}`)
  },
  alerts(page = 1, limit = 10, params?: { alert_type?: string; start_date?: string; end_date?: string; market_hash_name?: string }) {
    return api.get<AlertListResponse>('/alerts', { params: { page, limit, ...params } })
  },
  priceHistory(marketHashName: string, days?: number, platform?: string) {
    return api.get<PriceHistoryItem[]>(`/prices/${encodeURIComponent(marketHashName)}/history`, {
      params: { days, platform },
    })
  },
  platformPrices(marketHashName: string) {
    return api.get<PlatformPriceItem[]>(`/prices/${encodeURIComponent(marketHashName)}/platforms`)
  },
}
