"""FastAPI 应用入口."""

from __future__ import annotations

from pathlib import Path

import asyncio

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger

from config import MonitorConfig
from storage.database import Database
from web.routers import alerts, dashboard, extreme_track, kline, prices, settings, watchlist
from web.ws_manager import ws_manager


def create_app(db: Database, config: MonitorConfig) -> FastAPI:
    """创建并配置 FastAPI 应用."""
    app = FastAPI(
        title="CS2 Monitor API",
        description="CS2 饰品价格波动监控系统 Web API",
        version="1.0.0",
    )

    # 将 db 和 config 存入 app.state 供依赖注入使用
    app.state.db = db
    app.state.config = config

    # CORS：允许 Vite 开发服务器访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(watchlist.router, prefix="/api")
    app.include_router(alerts.router, prefix="/api")
    app.include_router(prices.router, prefix="/api")
    app.include_router(extreme_track.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(kline.router, prefix="/api")
    app.include_router(kline.arbitrage_router, prefix="/api")

    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        """健康检查端点."""
        return {"status": "ok"}

    # ------------------------------------------------------------------
    # WebSocket 端点
    # ------------------------------------------------------------------
    @app.websocket("/ws/alerts")
    async def ws_alerts(websocket: WebSocket) -> None:
        """实时告警推送 WebSocket."""
        ws_manager.set_loop(asyncio.get_running_loop())
        await ws_manager.connect_alert(websocket)
        try:
            while True:
                # 保持连接，等待客户端主动关闭或心跳超时
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except Exception:
            pass
        finally:
            ws_manager.disconnect_alert(websocket)

    @app.websocket("/ws/extreme-track/{market_hash_name}/{platform}")
    async def ws_extreme_track(
        websocket: WebSocket, market_hash_name: str, platform: str
    ) -> None:
        """极致追踪实时数据流 WebSocket."""
        ws_manager.set_loop(asyncio.get_running_loop())
        track_id = f"{market_hash_name}@{platform}"
        await ws_manager.connect_extreme_track(websocket, track_id)
        try:
            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except Exception:
            pass
        finally:
            ws_manager.disconnect_extreme_track(websocket, track_id)

    # 前端静态文件托管 + SPA fallback
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """提供前端静态文件，对不存在的路径回退到 index.html（SPA 支持）."""
        # API 路径交给上面的路由处理，这里不拦截
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(status_code=404, detail="Not found")

        # 如果请求的是存在的静态文件，直接返回
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # 否则返回 index.html，由 Vue Router 处理前端路由
        index_file = frontend_dist / "index.html"
        if not index_file.exists():
            raise HTTPException(
                status_code=500,
                detail="Frontend not built. Run: cd frontend && npm run build",
            )
        return FileResponse(str(index_file))

    if not frontend_dist.exists():
        logger.warning(
            f"前端构建产物不存在: {frontend_dist}，"
            "访问 http://localhost:8080/ 将看到 500 错误而非仪表盘"
        )

    return app
