"""价格数据路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from api.steamdt import SteamDTClient, SteamDTConfig
from config import MonitorConfig
from storage.database import Database
from web.deps import get_config, get_db, require_auth
from web.schemas import LatestPriceItem, PlatformPriceItem, PriceHistoryItem

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/search")
def search_item_price(
    q: str = Query(..., description="饰品 marketHashName"),
    db: Database = Depends(get_db),
    config: MonitorConfig = Depends(get_config),
    user: dict = Depends(require_auth),
) -> dict:
    """搜索饰品并返回各平台价格（通过 SteamDT API 实时查询）."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")

    steamdt_config = SteamDTConfig(
        api_key=config.api_key,
        base_url=config.api_base_url,
        timeout=config.request_timeout,
        max_retries=config.request_retry,
    )
    client = SteamDTClient(steamdt_config)
    try:
        response = client.get_items_batch([q.strip()])
        if not response.get("success"):
            raise HTTPException(
                status_code=502,
                detail=f"SteamDT API 错误: {response.get('errorMsg', '未知错误')}",
            )

        data = response.get("data") or []
        if not data:
            return {"market_hash_name": q, "dataList": [], "in_watchlist": db.get_watchlist_item(q) is not None}

        item = data[0]
        in_wl = db.get_watchlist_item(item.get("marketHashName", q)) is not None
        return {
            "market_hash_name": item.get("marketHashName", q),
            "dataList": item.get("dataList") or [],
            "in_watchlist": in_wl,
        }
    finally:
        client.close()


@router.get("/latest", response_model=list[LatestPriceItem])
def get_latest_prices(
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> list[dict]:
    """获取所有监控品的最新价格（每饰品每平台各取最新）."""
    return db.get_latest_prices()


@router.get("/{market_hash_name}/history", response_model=list[PriceHistoryItem])
def get_price_history(
    market_hash_name: str,
    days: int | None = None,
    platform: str | None = None,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
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
    user: dict = Depends(require_auth),
) -> list[dict]:
    """获取指定饰品在各平台的最新价格."""
    return db.get_price_by_platforms(market_hash_name)
