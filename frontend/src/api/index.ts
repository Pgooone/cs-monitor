import axios from 'axios'
import { toastError, toastWarning } from '@/composables/useToast'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request 拦截器：请求日志
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data || '')
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response 拦截器：错误处理 + 日志
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} -> ${response.status}`)
    }
    return response
  },
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.message || '未知错误'
    const url = error.config?.url || ''

    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.error(`[API] ${error.config?.method?.toUpperCase()} ${url} -> ${status}:`, detail)
    }

    if (status >= 500) {
      toastError(`服务器错误 (${status})：${detail}`)
    } else if (status === 429) {
      toastWarning('请求过于频繁，请稍后再试')
    }

    return Promise.reject(error)
  },
)

export interface VolatileItem {
  market_hash_name: string
  display_name: string | null
  current_price: number | null
  change_percent: number
  sparkline: number[]
}

export interface DashboardSummary {
  active_watchlist: number
  extreme_track_count: number
  today_alert_count: number
  yesterday_alert_count: number
  latest_price_count: number
  last_update: string | null
  today_collection_count: number
  check_interval_minutes: number
  portfolio_history: { date: string; value: number }[]
  top_volatile: VolatileItem[]
  api_quota_percent: number
  watchlist_sparkline: number[]
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

export interface PlatformPriceMini {
  platform: string
  price: number
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
  change_24h: number | null
  sparkline: number[]
  platform_prices: PlatformPriceMini[]
  icon_url?: string | null
  created_at: string | null
  updated_at: string | null
}

export interface AlertRecord {
  id: number
  market_hash_name: string
  display_name: string | null
  alert_type: string
  current_price: number | null
  baseline_price: number | null
  change_percent: number | null
  notified_at: string
}

export interface ExtremeAlertRecord {
  id: number
  market_hash_name: string
  display_name: string | null
  platform: string
  alert_type: string
  prev_price: number | null
  curr_price: number | null
  price_change_percent: number | null
  prev_quantity: number | null
  curr_quantity: number | null
  quantity_change_percent: number | null
  notified_at: string
}

export interface AlertListResponse {
  items: AlertRecord[]
  total: number
  page: number
  limit: number
}

export interface ExtremeAlertListResponse {
  items: ExtremeAlertRecord[]
  total: number
  page: number
  limit: number
}

export interface AlertStatsItem {
  date: string
  alert_type: string
  count: number
}

export interface AlertStatsResponse {
  total: number
  by_day: AlertStatsItem[]
  by_type: AlertStatsItem[]
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

export interface ExtremeTrackConfig {
  id: number
  market_hash_name: string
  display_name: string | null
  platform: string
  interval_seconds: number
  enabled: number
  price_track_enabled: number
  price_change_mode: string
  price_threshold_percent: number
  quantity_track_enabled: number
  quantity_change_mode: string
  quantity_threshold_percent: number
  alert_cooldown_seconds: number
  quiet_hours_start: string | null
  quiet_hours_end: string | null
  icon_url?: string | null
  created_at: string | null
  updated_at: string | null
}

export interface CreateExtremeTrackPayload {
  market_hash_name: string
  platform: string
  interval_seconds?: number
  enabled?: boolean
  price_track_enabled?: boolean
  price_change_mode?: string
  price_threshold_percent?: number
  quantity_track_enabled?: boolean
  quantity_change_mode?: string
  quantity_threshold_percent?: number
  alert_cooldown_seconds?: number
  quiet_hours_start?: string | null
  quiet_hours_end?: string | null
}

export interface UpdateExtremeTrackPayload {
  interval_seconds?: number
  enabled?: boolean
  price_track_enabled?: boolean
  price_change_mode?: string
  price_threshold_percent?: number
  quantity_track_enabled?: boolean
  quantity_change_mode?: string
  quantity_threshold_percent?: number
  alert_cooldown_seconds?: number
  quiet_hours_start?: string | null
  quiet_hours_end?: string | null
}

export interface NotifySettings {
  notify_channel: string
  wecom_webhook_url: string
  telegram_bot_token: string
  telegram_chat_id: string
  serverchan_sendkey: string
}

export interface KlineDataItem {
  date: string
  open: number
  close: number
  high: number
  low: number
  volume: number
}

export interface KlineResponse {
  market_hash_name: string
  period: number
  data: KlineDataItem[]
}

export interface ArbitrageItem {
  market_hash_name: string
  min_price: number
  min_platform: string
  max_price: number
  max_platform: string
  spread: number
  spread_percent: number
  platforms: PlatformPriceItem[]
}

export interface DailyPricePoint {
  date: string
  price: number
}

export interface TrendAnalysisResponse {
  market_hash_name: string
  trend: string
  daily_prices: DailyPricePoint[]
  ma5: (number | null)[]
  ma10: (number | null)[]
  ma20: (number | null)[]
}

export interface RefreshItemResult {
  market_hash_name: string
  ok: boolean
  latest_price: number | null
  platform_count: number
  error: string | null
}

export interface RefreshResponse {
  total: number
  success: number
  failed: number
  duration_ms: number
  items: RefreshItemResult[]
}

/** 本地搜索结果项 */
export interface SearchItemResult {
  market_hash_name: string
  name: string | null
  icon_url?: string | null
}

/** 实时价格查询结果 */
export interface ItemPriceResult {
  market_hash_name: string
  display_name: string | null
  dataList: { platform: string; sellPrice: number }[]
  in_watchlist: boolean
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
  alertStats(params?: { start_date?: string; end_date?: string }) {
    return api.get<AlertStatsResponse>('/alerts/stats', { params })
  },
  extremeAlerts(page = 1, limit = 10, params?: { alert_type?: string; start_date?: string; end_date?: string; market_hash_name?: string }) {
    return api.get<ExtremeAlertListResponse>('/extreme-track/alerts', { params: { page, limit, ...params } })
  },
  priceHistory(marketHashName: string, days?: number, platform?: string) {
    return api.get<PriceHistoryItem[]>(`/prices/${encodeURIComponent(marketHashName)}/history`, {
      params: { days, platform },
    })
  },
  platformPrices(marketHashName: string) {
    return api.get<PlatformPriceItem[]>(`/prices/${encodeURIComponent(marketHashName)}/platforms`)
  },
  extremeTrackList() {
    return api.get<ExtremeTrackConfig[]>('/extreme-track')
  },
  extremeTrackSnapshots() {
    return api.get<{ market_hash_name: string; platform: string; price: number; quantity: number; recorded_at: string }[]>('/extreme-track/snapshots')
  },
  createExtremeTrack(payload: CreateExtremeTrackPayload) {
    return api.post<ExtremeTrackConfig>('/extreme-track', payload)
  },
  updateExtremeTrack(marketHashName: string, platform: string, payload: UpdateExtremeTrackPayload) {
    return api.put<ExtremeTrackConfig>(`/extreme-track/${encodeURIComponent(marketHashName)}/${encodeURIComponent(platform)}`, payload)
  },
  deleteExtremeTrack(marketHashName: string, platform: string) {
    return api.delete(`/extreme-track/${encodeURIComponent(marketHashName)}/${encodeURIComponent(platform)}`)
  },
  toggleExtremeTrack(marketHashName: string, platform: string) {
    return api.post(`/extreme-track/${encodeURIComponent(marketHashName)}/${encodeURIComponent(platform)}/toggle`)
  },
  getNotifySettings() {
    return api.get<NotifySettings>('/settings/notify')
  },
  updateNotifySettings(payload: Partial<NotifySettings>) {
    return api.put('/settings/notify', payload)
  },
  testNotify(channel?: string, extra?: Record<string, any>) {
    return api.post('/settings/notify/test', { channel, extra })
  },
  systemInfo() {
    return api.get<{ version: string; db_path: string; db_size: number; db_size_human: string; data_dir: string; watchlist_count: number; extreme_track_count: number }>('/settings/system')
  },
  exportDb() {
    return api.get('/settings/db/export', { responseType: 'blob' })
  },
  clearDb() {
    return api.post('/settings/db/clear?confirm=true')
  },
  kline(marketHashName: string, period?: number, count?: number) {
    return api.get<KlineResponse>(`/kline/${encodeURIComponent(marketHashName)}`, {
      params: { period, count },
    })
  },
  arbitrage() {
    return api.get<ArbitrageItem[]>('/arbitrage')
  },
  arbitrageItem(marketHashName: string) {
    return api.get<ArbitrageItem>(`/arbitrage/${encodeURIComponent(marketHashName)}`)
  },
  trends(marketHashName: string, days?: number) {
    return api.get<TrendAnalysisResponse>(`/trends/${encodeURIComponent(marketHashName)}`, {
      params: { days },
    })
  },
  searchItemPrice(q: string) {
    return api.get('/prices/search', { params: { q } })
  },
  /** 本地模糊搜索饰品（不查实时价格） */
  searchItems(q: string, limit = 20) {
    return api.get<SearchItemResult[]>('/prices/search', { params: { q, limit } })
  },
  /** 通过精确 marketHashName 查实时价格 */
  lookupItemPrice(marketHashName: string) {
    return api.get<ItemPriceResult>('/prices/lookup', { params: { market_hash_name: marketHashName } })
  },
  refreshWatchlist(marketHashNames?: string[] | null) {
    return api.post<RefreshResponse>('/watchlist/refresh', {
      market_hash_names: marketHashNames ?? null,
    })
  },
  /** 获取饰品图标 URL（优先数据库缓存） */
  getItemIcon(marketHashName: string) {
    return api.get<{ market_hash_name: string; icon_url: string | null }>(
      `/prices/items/${encodeURIComponent(marketHashName)}/icon`,
    )
  },
  /** 批量同步所有缺少图标的饰品 */
  syncItemIcons() {
    return api.post<{ synced: number; total: number; message?: string }>('/prices/items/icons/sync')
  },
}
