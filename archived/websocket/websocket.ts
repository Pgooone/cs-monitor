/**
 * WebSocket 全局状态管理
 *
 * 管理告警和极致追踪的 WS 连接状态，支持自动重连、心跳、右下角状态展示。
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type WsStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

interface WsConnection {
  url: string
  ws: WebSocket | null
  status: WsStatus
  lastPingAt: number
  reconnectCount: number
}

const WS_BASE_URL = (() => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return `${protocol}//${host}`
})()

const MAX_RECONNECT = 5
const RECONNECT_INTERVAL = 3000
const HEARTBEAT_INTERVAL = 30000

export const useWebsocketStore = defineStore('websocket', () => {
  // 告警频道
  const alertConn = ref<WsConnection>({
    url: '',
    ws: null,
    status: 'idle',
    lastPingAt: 0,
    reconnectCount: 0,
  })

  // 极致追踪频道（key: trackId）
  const extremeConns = ref<Map<string, WsConnection>>(new Map())

  const overallStatus = computed<WsStatus>(() => {
    const conns = [alertConn.value, ...extremeConns.value.values()]
    if (conns.some((c) => c.status === 'error')) return 'error'
    if (conns.some((c) => c.status === 'connecting')) return 'connecting'
    if (conns.some((c) => c.status === 'connected')) return 'connected'
    if (conns.some((c) => c.status === 'disconnected')) return 'disconnected'
    return 'idle'
  })

  const activeConnectionCount = computed(() => {
    let count = 0
    if (alertConn.value.status === 'connected') count++
    extremeConns.value.forEach((c) => {
      if (c.status === 'connected') count++
    })
    return count
  })

  // 心跳定时器
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null

  function startHeartbeat() {
    if (heartbeatTimer) return
    heartbeatTimer = setInterval(() => {
      const now = Date.now()
      // 告警频道心跳
      if (alertConn.value.ws && alertConn.value.status === 'connected') {
        if (now - alertConn.value.lastPingAt > HEARTBEAT_INTERVAL) {
          alertConn.value.ws.send('ping')
          alertConn.value.lastPingAt = now
        }
      }
      // 极致追踪频道心跳
      extremeConns.value.forEach((conn) => {
        if (conn.ws && conn.status === 'connected') {
          if (now - conn.lastPingAt > HEARTBEAT_INTERVAL) {
            conn.ws.send('ping')
            conn.lastPingAt = now
          }
        }
      })
    }, HEARTBEAT_INTERVAL)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  function _createConnection(
    url: string,
    onMessage: (data: unknown) => void,
    existing?: WsConnection,
  ): WsConnection {
    const fullUrl = url

    const conn: WsConnection = {
      url,
      ws: new WebSocket(fullUrl),
      status: 'connecting',
      lastPingAt: Date.now(),
      reconnectCount: existing?.reconnectCount ?? 0,
    }

    const ws = conn.ws
    if (!ws) return conn

    ws.onopen = () => {
      conn.status = 'connected'
      conn.reconnectCount = 0
      conn.lastPingAt = Date.now()
      startHeartbeat()
    }

    ws.onmessage = (event) => {
      if (event.data === 'pong') {
        conn.lastPingAt = Date.now()
        return
      }
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch {
        onMessage(event.data)
      }
    }

    ws.onerror = () => {
      conn.status = 'error'
    }

    ws.onclose = () => {
      if (conn.status !== 'error') {
        conn.status = 'disconnected'
      }
      // 自动重连
      if (conn.reconnectCount < MAX_RECONNECT) {
        conn.reconnectCount++
        setTimeout(() => {
          const reconn = _createConnection(url, onMessage, conn)
          // 将新连接替换旧引用
          if (alertConn.value.url === url) {
            alertConn.value = reconn
          } else {
            extremeConns.value.set(url, reconn)
          }
        }, RECONNECT_INTERVAL)
      }
    }

    return conn
  }

  /** 连接告警推送频道 */
  function connectAlerts(onMessage: (data: unknown) => void) {
    disconnectAlerts()
    const url = `${WS_BASE_URL}/ws/alerts`
    alertConn.value = _createConnection(url, onMessage)
    alertConn.value.url = url
  }

  /** 断开告警推送 */
  function disconnectAlerts() {
    if (alertConn.value.ws) {
      alertConn.value.ws.close()
    }
    alertConn.value = {
      url: '',
      ws: null,
      status: 'idle',
      lastPingAt: 0,
      reconnectCount: 0,
    }
    // 如果没有其他连接，停止心跳
    if (extremeConns.value.size === 0) {
      stopHeartbeat()
    }
  }

  /** 连接极致追踪频道 */
  function connectExtremeTrack(
    marketHashName: string,
    platform: string,
    onMessage: (data: unknown) => void,
  ) {
    const trackId = `${marketHashName}@${platform}`
    const url = `${WS_BASE_URL}/ws/extreme-track/${encodeURIComponent(marketHashName)}/${encodeURIComponent(platform)}`

    const existing = extremeConns.value.get(trackId)
    if (existing?.ws) {
      existing.ws.close()
    }

    const conn = _createConnection(url, onMessage, existing)
    conn.url = url
    extremeConns.value.set(trackId, conn)
  }

  /** 断开极致追踪频道 */
  function disconnectExtremeTrack(marketHashName: string, platform: string) {
    const trackId = `${marketHashName}@${platform}`
    const conn = extremeConns.value.get(trackId)
    if (conn?.ws) {
      conn.ws.close()
    }
    extremeConns.value.delete(trackId)
    if (alertConn.value.status === 'idle' && extremeConns.value.size === 0) {
      stopHeartbeat()
    }
  }

  /** 断开所有 WS */
  function disconnectAll() {
    disconnectAlerts()
    extremeConns.value.forEach((conn) => {
      if (conn.ws) conn.ws.close()
    })
    extremeConns.value.clear()
    stopHeartbeat()
  }

  return {
    alertConn,
    extremeConns,
    overallStatus,
    activeConnectionCount,
    connectAlerts,
    disconnectAlerts,
    connectExtremeTrack,
    disconnectExtremeTrack,
    disconnectAll,
  }
})
