"""FastAPI 应用入口."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import MonitorConfig
from storage.database import Database
from web.routers import alerts, dashboard, extreme_track, prices, settings, watchlist


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

    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        """健康检查端点."""
        return {"status": "ok"}

    return app
