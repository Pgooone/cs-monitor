/** WebSocket 客户端封装 */

export interface WebSocketClientOptions {
  url: string
  onMessage?: (msg: any) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (err: Event) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export class WebSocketClient {
  private url: string
  private onMessage?: (msg: any) => void
  private onOpen?: () => void
  private onClose?: () => void
  private onError?: (err: Event) => void
  private reconnectInterval: number
  private maxReconnectAttempts: number
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private shouldReconnect = true

  constructor(options: WebSocketClientOptions) {
    this.url = options.url
    this.onMessage = options.onMessage
    this.onOpen = options.onOpen
    this.onClose = options.onClose
    this.onError = options.onError
    this.reconnectInterval = options.reconnectInterval ?? 3000
    this.maxReconnectAttempts = options.maxReconnectAttempts ?? 10
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return

    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        this.reconnectAttempts = 0
        this.onOpen?.()
      }

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          this.onMessage?.(msg)
        } catch {
          // 忽略非 JSON 消息
        }
      }

      this.ws.onclose = () => {
        this.onClose?.()
        this.tryReconnect()
      }

      this.ws.onerror = (err) => {
        this.onError?.(err)
      }
    } catch {
      this.tryReconnect()
    }
  }

  private tryReconnect() {
    if (!this.shouldReconnect) return
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return

    this.reconnectAttempts++
    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, this.reconnectInterval)
  }

  close() {
    this.shouldReconnect = false
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}
