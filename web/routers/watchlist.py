"""监控清单路由."""

from __future__ import annotations

import time as _time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from api.steamdt import (
    SteamDTBusinessError,
    SteamDTClient,
    SteamDTConfig,
    SteamDTError,
    SteamDTRateLimitError,
)
from config import MonitorConfig
from storage.database import Database
from web.deps import get_config, get_db, require_auth
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
    if result is None:
        raise HTTPException(status_code=404, detail="饰品不存在")
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


# ─── /refresh 端点 ─────────────────────────────────────


class RefreshRequest(BaseModel):
    market_hash_names: Optional[list[str]] = Field(
        default=None,
        description="为空或不传则刷新所有 enabled 物品，最多 100 个",
    )


class RefreshItemResult(BaseModel):
    market_hash_name: str
    ok: bool
    latest_price: Optional[float] = None
    platform_count: int = 0
    error: Optional[str] = None


class RefreshResponse(BaseModel):
    total: int
    success: int
    failed: int
    duration_ms: int
    items: list[RefreshItemResult]


def _get_steamdt_client(request: Request, config: MonitorConfig) -> SteamDTClient:
    """从 app.state 取共享 client；不存在则惰性创建一个并缓存."""
    client = getattr(request.app.state, "steamdt_client", None)
    if client is None:
        client = SteamDTClient(SteamDTConfig(
            api_key=config.api_key,
            base_url=config.api_base_url,
            timeout=config.request_timeout,
            max_retries=config.request_retry,
        ))
        request.app.state.steamdt_client = client
    return client


@router.post("/refresh", response_model=RefreshResponse)
def refresh_watchlist_prices(
    payload: RefreshRequest,
    request: Request,
    db: Database = Depends(get_db),
    config: MonitorConfig = Depends(get_config),
    user: dict = Depends(require_auth),
) -> RefreshResponse:
    """立即刷新指定物品（或全部）的价格.

    使用 SteamDT batch 端点（1 次/分钟限制），单次最多 100 个.
    """
    # 1) 解析目标列表
    if payload.market_hash_names:
        names = list(dict.fromkeys(payload.market_hash_names))  # 去重保序
    else:
        watchlist = db.get_watchlist(enabled_only=True)
        names = [
            it["market_hash_name"]
            for it in watchlist
            if it.get("market_hash_name")
        ]

    if not names:
        return RefreshResponse(total=0, success=0, failed=0, duration_ms=0, items=[])

    if len(names) > 100:
        raise HTTPException(
            status_code=400,
            detail=f"单次最多刷新 100 个，您选了 {len(names)} 个。请分批操作或取消部分选中。",
        )

    # 2) 调 SteamDT batch
    client = _get_steamdt_client(request, config)
    started = _time.monotonic()

    try:
        response = client.get_items_batch(names, use_throttle=True)
    except SteamDTRateLimitError as e:
        retry_after = int(e.retry_after) + 1
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limited",
                "source": e.source,
                "retry_after": retry_after,
                "message": f"刷新过于频繁，请 {retry_after} 秒后再试",
            },
            headers={"Retry-After": str(retry_after)},
        )
    except SteamDTBusinessError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SteamDT 业务错误 [{e.code}]: {e.error_msg}",
        )
    except SteamDTError as e:
        raise HTTPException(status_code=502, detail=f"SteamDT 调用失败: {e}")

    # 3) 解析响应 + 写快照
    data_list = response.get("data") or []
    by_name = {
        it.get("marketHashName"): it
        for it in data_list
        if it.get("marketHashName")
    }

    results: list[RefreshItemResult] = []
    for name in names:
        item = by_name.get(name)
        if not item:
            results.append(RefreshItemResult(
                market_hash_name=name, ok=False, error="not_found_in_response"
            ))
            continue

        # 确保 items 表有外键记录
        db.insert_item(name)

        platform_data = item.get("dataList") or []
        prices: list[float] = []
        for p in platform_data:
            platform = p.get("platform")
            sell_price = p.get("sellPrice")
            if platform is None or sell_price is None:
                continue
            try:
                price_f = float(sell_price)
            except (TypeError, ValueError):
                continue
            db.insert_price_record(name, platform, price_f)
            if price_f > 0:
                prices.append(price_f)

        latest = min(prices) if prices else None
        results.append(RefreshItemResult(
            market_hash_name=name,
            ok=latest is not None,
            latest_price=latest,
            platform_count=len(prices),
            error=None if latest is not None else "no_valid_platform_price",
        ))

    duration_ms = int((_time.monotonic() - started) * 1000)
    success_count = sum(1 for r in results if r.ok)

    return RefreshResponse(
        total=len(names),
        success=success_count,
        failed=len(names) - success_count,
        duration_ms=duration_ms,
        items=results,
    )
