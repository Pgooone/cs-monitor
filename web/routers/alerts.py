"""告警记录路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from storage.database import Database
from web.schemas import AlertRecord, AlertRecordFilter, AlertStatsItem, AlertStatsResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_db(request: Request) -> Database:
    """依赖注入：数据库实例."""
    return request.app.state.db


@router.get("", response_model=list[AlertRecord])
def get_alerts(
    page: int = 1,
    limit: int = 20,
    alert_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    market_hash_name: str | None = None,
    db: Database = Depends(get_db),
) -> list[dict]:
    """分页查询告警记录.

    支持参数：
    - page: 页码（默认1）
    - limit: 每页数量（默认20，最大100）
    - alert_type: 告警类型过滤
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - market_hash_name: 饰品名称模糊匹配
    """
    rows, _ = db.get_alerts(
        page=page,
        limit=limit,
        alert_type=alert_type,
        start_date=start_date,
        end_date=end_date,
        market_hash_name=market_hash_name,
    )
    return rows


@router.get("/stats", response_model=AlertStatsResponse)
def get_alert_stats(
    start_date: str | None = None,
    end_date: str | None = None,
    db: Database = Depends(get_db),
) -> dict:
    """告警统计（按天/类型聚合）.

    支持参数：
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    """
    by_day_raw, by_type_raw = db.get_alert_stats(
        start_date=start_date,
        end_date=end_date,
    )

    by_day = [
        AlertStatsItem(
            date=str(row["date"]),
            alert_type=row["alert_type"],
            count=row["count"],
        )
        for row in by_day_raw
    ]

    by_type = [
        AlertStatsItem(
            date=str(row["date"]),
            alert_type=row["alert_type"],
            count=row["count"],
        )
        for row in by_type_raw
    ]

    total = sum(item.count for item in by_type)

    return {
        "total": total,
        "by_day": by_day,
        "by_type": by_type,
    }
