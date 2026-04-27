"""价格数据路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from api.steamdt import SteamDTClient, SteamDTBusinessError, SteamDTError, SteamDTRateLimitError
from storage.database import Database
from web.deps import get_db, require_auth
from web.schemas import LatestPriceItem, PlatformPriceItem, PriceHistoryItem

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/search")
def search_items_local(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回数量上限"),
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> list[dict]:
    """本地模糊搜索饰品（FTS5 全文搜索 + LIKE 兜底）.

    返回匹配的饰品列表（market_hash_name + name），不查实时价格。
    用户选择后再调用 /prices/lookup 查实时价格。
    """
    if not q.strip():
        return []
    return db.search_items(q.strip(), limit=limit)


@router.get("/lookup")
def lookup_item_price(
    market_hash_name: str = Query(..., description="精确的 marketHashName"),
    request: Request = None,  # type: ignore[assignment]
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """通过精确 marketHashName 查询饰品各平台实时价格."""
    if not market_hash_name.strip():
        raise HTTPException(status_code=400, detail="market_hash_name 不能为空")

    client: SteamDTClient = request.app.state.steamdt_client
    name = market_hash_name.strip()
    try:
        response = client.get_item_price_single(name)
    except SteamDTRateLimitError as e:
        retry_after = int(e.retry_after) + 1
        raise HTTPException(
            status_code=429,
            detail={"error": "rate_limited", "retry_after": retry_after},
            headers={"Retry-After": str(retry_after)},
        )
    except SteamDTBusinessError as e:
        raise HTTPException(status_code=502, detail=f"[{e.code}] {e.error_msg}")
    except SteamDTError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if not response.get("success"):
        raise HTTPException(
            status_code=502,
            detail=f"SteamDT API 错误: {response.get('errorMsg', '未知错误')}",
        )

    # /price/single 返回 data 是平台价格数组（不是 batch 那样的 {marketHashName, dataList}）
    data_list = response.get("data") or []
    if not isinstance(data_list, list):
        data_list = []

    in_wl = db.get_watchlist_item(market_hash_name) is not None
    return {
        "market_hash_name": market_hash_name,
        "dataList": data_list,
        "in_watchlist": in_wl,
    }


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
