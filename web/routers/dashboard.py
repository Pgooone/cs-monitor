"""Dashboard 概览路由."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from config import MonitorConfig
from storage.database import Database
from web.deps import get_config, get_db, require_auth
from web.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Database = Depends(get_db),
    config: MonitorConfig = Depends(get_config),
    user: dict = Depends(require_auth),
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

    # 计算昨日告警数
    yesterday_alert_count = 0
    try:
        yesterday_start = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday_start.strftime("%Y-%m-%d")
        _, by_day = db.get_alert_stats(start_date=yesterday_str, end_date=yesterday_str)
        yesterday_alert_count = sum(d["count"] for d in by_day)
    except Exception:
        pass

    return DashboardSummary(
        active_watchlist=db.get_watchlist_count(enabled_only=True),
        extreme_track_count=db.get_extreme_track_count(enabled_only=True),
        today_alert_count=today_alert_count,
        yesterday_alert_count=yesterday_alert_count,
        latest_price_count=latest_price_count,
        last_update=last_update,
        today_collection_count=db.get_today_collection_count(),
        check_interval_minutes=30,
        portfolio_history=[],
        top_volatile=[],
        api_quota_percent=0.0,
        watchlist_sparkline=[],
    )
