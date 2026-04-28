"""价格数据路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from api.steam_images import fetch_icon_url, fetch_icon_urls_batch
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


@router.get("/items/{market_hash_name:path}/icon")
async def get_item_icon(market_hash_name: str, db: Database = Depends(get_db)):
    """获取饰品图标 URL，优先从数据库缓存读取.

    若数据库无缓存则从 Steam 社区市场获取并写入数据库。
    """
    icon_url = db.get_item_icon_url(market_hash_name)
    if not icon_url:
        icon_url = await fetch_icon_url(market_hash_name)
        if icon_url:
            db.update_item_icon_url(market_hash_name, icon_url)
    return {"market_hash_name": market_hash_name, "icon_url": icon_url}


@router.post("/items/icons/sync")
async def sync_item_icons(db: Database = Depends(get_db)):
    """批量同步所有缺少图标的饰品 icon_url.

    查询 items 表中 icon_url 为空的记录，逐个从 Steam 社区市场获取并更新。
    """
    with db._cursor() as cursor:
        # 从 items 和 watchlist 两张表获取需要同步图标的饰品
        cursor.execute(
            """
            SELECT DISTINCT market_hash_name FROM (
                SELECT market_hash_name FROM items WHERE icon_url IS NULL OR icon_url = ''
                UNION
                SELECT market_hash_name FROM watchlist WHERE market_hash_name NOT IN (
                    SELECT market_hash_name FROM items WHERE icon_url IS NOT NULL AND icon_url != ''
                )
            )
            """
        )
        items = cursor.fetchall()

    if not items:
        return {"synced": 0, "total": 0, "message": "所有饰品已有图标"}

    names = [row[0] for row in items]
    results = await fetch_icon_urls_batch(names)

    synced = 0
    for name, url in results.items():
        if url:
            db.update_item_icon_url(name, url)
            synced += 1

    return {"synced": synced, "total": len(names)}
