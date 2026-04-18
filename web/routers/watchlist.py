"""监控清单路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from storage.database import Database
from web.deps import get_db, require_auth
from web.schemas import (
    WatchlistItem,
    WatchlistItemCreate,
    WatchlistItemUpdate,
    WatchlistItemWithPrice,
)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemWithPrice])
def get_watchlist(
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> list[dict]:
    """获取全部监控清单（含最新价格）."""
    return db.get_watchlist_with_latest_price(enabled_only=False)


@router.post("", response_model=WatchlistItem)
def create_watchlist_item(
    item: WatchlistItemCreate,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """添加监控清单项."""
    existing = db.get_watchlist_item(item.market_hash_name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"饰品 '{item.market_hash_name}' 已在监控清单中",
        )
    db.insert_watchlist_item(
        market_hash_name=item.market_hash_name,
        display_name=item.display_name,
        threshold_percent=item.threshold_percent,
        enabled=item.enabled,
    )
    result = db.get_watchlist_item(item.market_hash_name)
    if not result:
        raise HTTPException(status_code=500, detail="创建失败")
    return dict(result)


@router.put("/{market_hash_name}", response_model=WatchlistItem)
def update_watchlist_item(
    market_hash_name: str,
    item: WatchlistItemUpdate,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """更新监控清单项."""
    existing = db.get_watchlist_item(market_hash_name)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"饰品 '{market_hash_name}' 不存在",
        )
    db.update_watchlist_item(
        market_hash_name=market_hash_name,
        display_name=item.display_name,
        threshold_percent=item.threshold_percent,
        enabled=item.enabled,
    )
    result = db.get_watchlist_item(market_hash_name)
    return dict(result)


@router.delete("/{market_hash_name}")
def delete_watchlist_item(
    market_hash_name: str,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """删除监控清单项."""
    existing = db.get_watchlist_item(market_hash_name)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"饰品 '{market_hash_name}' 不存在",
        )
    db.delete_watchlist_item(market_hash_name)
    return {"message": f"已删除 '{market_hash_name}'"}
