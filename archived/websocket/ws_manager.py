"""WebSocket 连接管理器."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    """管理 WebSocket 连接，支持按频道广播."""

    def __init__(self) -> None:
        self._alert_connections: list[WebSocket] = []
        self._extreme_connections: dict[str, list[WebSocket]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """设置事件循环（用于从其他线程安全广播）."""
        self._loop = loop

    # ------------------------------------------------------------------
    # Alerts 频道
    # ------------------------------------------------------------------
    async def connect_alert(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._alert_connections.append(websocket)
        logger.debug(f"WebSocket /ws/alerts 连接建立，当前连接数: {len(self._alert_connections)}")

    def disconnect_alert(self, websocket: WebSocket) -> None:
        if websocket in self._alert_connections:
            self._alert_connections.remove(websocket)
            logger.debug(f"WebSocket /ws/alerts 连接断开，当前连接数: {len(self._alert_connections)}")

    async def broadcast_alert(self, message: dict[str, Any]) -> None:
        """异步广播告警消息（在事件循环中调用）."""
        dead: list[WebSocket] = []
        for ws in list(self._alert_connections):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_alert(ws)

    def broadcast_alert_sync(self, message: dict[str, Any]) -> None:
        """同步广播告警消息（从非事件循环线程调用）."""
        if not self._loop:
            return
        for ws in list(self._alert_connections):
            try:
                asyncio.run_coroutine_threadsafe(ws.send_json(message), self._loop)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Extreme Track 频道
    # ------------------------------------------------------------------
    async def connect_extreme_track(self, websocket: WebSocket, track_id: str) -> None:
        await websocket.accept()
        self._extreme_connections.setdefault(track_id, []).append(websocket)
        logger.debug(
            f"WebSocket /ws/extreme-track/{track_id} 连接建立"
        )

    def disconnect_extreme_track(self, websocket: WebSocket, track_id: str) -> None:
        conns = self._extreme_connections.get(track_id, [])
        if websocket in conns:
            conns.remove(websocket)
            logger.debug(
                f"WebSocket /ws/extreme-track/{track_id} 连接断开"
            )

    async def broadcast_extreme_track(
        self, track_id: str, message: dict[str, Any]
    ) -> None:
        """异步广播极致追踪消息."""
        conns = self._extreme_connections.get(track_id, [])
        dead: list[WebSocket] = []
        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_extreme_track(ws, track_id)

    def broadcast_extreme_track_sync(
        self, track_id: str, message: dict[str, Any]
    ) -> None:
        """同步广播极致追踪消息（从非事件循环线程调用）."""
        if not self._loop:
            return
        conns = self._extreme_connections.get(track_id, [])
        for ws in list(conns):
            try:
                asyncio.run_coroutine_threadsafe(ws.send_json(message), self._loop)
            except Exception:
                pass


# 全局单例
ws_manager = WebSocketManager()
