export type WSMessageHandler = (data: any) => void

interface WSOptions {
  url: string
  onMessage?: WSMessageHandler
  onOpen?: () => void
  onClose?: () => void
  onError?: (e: Event) => void
  heartbeatInterval?: number
  reconnectInterval?: number
  maxReconnectInterval?: number
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private onMessage?: WSMessageHandler
  private onOpen?: () => void
  private onClose?: () => void
  private onError?: (e: Event) => void
  private heartbeatInterval: number
  private reconnectInterval: number
  private maxReconnectInterval: number
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private closed = false
  private currentReconnectInterval: number

  constructor(options: WSOptions) {
    this.url = options.url
    this.onMessage = options.onMessage
    this.onOpen = options.onOpen
    this.onClose = options.onClose
    this.onError = options.onError
    this.heartbeatInterval = options.heartbeatInterval ?? 30000
    this.reconnectInterval = options.reconnectInterval ?? 3000
    this.maxReconnectInterval = options.maxReconnectInterval ?? 30000
    this.currentReconnectInterval = this.reconnectInterval
  }

  connect() {
    if (this.closed || this.ws?.readyState === WebSocket.OPEN) return

    try {
      this.ws = new WebSocket(this.url)
    } catch (e) {
      this.scheduleReconnect()
      return
    }

    this.ws.onopen = () => {
      this.currentReconnectInterval = this.reconnectInterval
      this.onOpen?.()
      this.startHeartbeat()
    }

    this.ws.onmessage = (event) => {
      if (event.data === 'pong') return
      try {
        const parsed = JSON.parse(event.data)
        this.onMessage?.(parsed)
      } catch {
        this.onMessage?.(event.data)
      }
    }

    this.ws.onclose = () => {
      this.stopHeartbeat()
      this.onClose?.()
      this.scheduleReconnect()
    }

    this.ws.onerror = (e) => {
      this.onError?.(e)
    }
  }

  private startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send('ping')
      }
    }, this.heartbeatInterval)
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private scheduleReconnect() {
    if (this.closed) return
    if (this.reconnectTimer) return
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, this.currentReconnectInterval)
    this.currentReconnectInterval = Math.min(
      this.currentReconnectInterval * 2,
      this.maxReconnectInterval,
    )
  }

  send(data: string | object) {
    if (this.ws?.readyState !== WebSocket.OPEN) return
    const payload = typeof data === 'string' ? data : JSON.stringify(data)
    this.ws.send(payload)
  }

  close() {
    this.closed = true
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
