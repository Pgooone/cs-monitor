"""价格数据路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from storage.database import Database
from web.schemas import LatestPriceItem, PlatformPriceItem, PriceHistoryItem

router = APIRouter(prefix="/prices", tags=["prices"])


def get_db(request: Request) -> Database:
    """依赖注入：数据库实例."""
    return request.app.state.db


@router.get("/latest", response_model=list[LatestPriceItem])
def get_latest_prices(
    db: Database = Depends(get_db),
) -> list[dict]:
    """获取所有监控品的最新价格（每饰品每平台各取最新）."""
    return db.get_latest_prices()


@router.get("/{market_hash_name}/history", response_model=list[PriceHistoryItem])
def get_price_history(
    market_hash_name: str,
    days: int | None = None,
    platform: str | None = None,
    db: Database = Depends(get_db),
) -> list[dict]:
    """获取指定饰品的历史价格记录.

    支持参数：
    - days: 查询最近 N 天的数据
    - platform: 按平台过滤
    """
    return db.get_price_history(
        market_hash_name=market_hash_name,
        days=days,
        platform=platform,
    )


@router.get("/{market_hash_name}/platforms", response_model=list[PlatformPriceItem])
def get_price_by_platforms(
    market_hash_name: str,
    db: Database = Depends(get_db),
) -> list[dict]:
    """获取指定饰品在各平台的最新价格."""
    return db.get_price_by_platforms(market_hash_name)
