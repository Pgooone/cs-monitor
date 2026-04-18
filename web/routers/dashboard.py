"""Dashboard 概览路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from config import MonitorConfig
from storage.database import Database
from web.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_db(request: Request) -> Database:
    """依赖注入：数据库实例."""
    return request.app.state.db


def get_config(request: Request) -> MonitorConfig:
    """依赖注入：配置实例."""
    return request.app.state.config


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Database = Depends(get_db),
    config: MonitorConfig = Depends(get_config),
) -> DashboardSummary:
    """返回 Dashboard 概览数据."""
    today_alert_count = db.get_today_alert_count()
    latest_price_count = db.get_latest_price_records_count()

    # 获取最近一条价格记录的更新时间
    latest_record = db.get_latest_price_record_any()
    last_update = None
    if latest_record:
        recorded_at = latest_record.get("recorded_at")
        if recorded_at:
            last_update = str(recorded_at)

    return DashboardSummary(
        active_watchlist=len(config.watchlist),
        extreme_track_count=len(config.extreme_track_list),
        today_alert_count=today_alert_count,
        latest_price_count=latest_price_count,
        last_update=last_update,
    )
