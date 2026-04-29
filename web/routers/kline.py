"""K 线、价差与趋势路由."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from api.steamdt import (
    SteamDTBusinessError,
    SteamDTError,
    SteamDTRateLimitError,
)
from core.trend_analyzer import TrendAnalyzer
from storage.database import Database
from web.deps import get_config, get_db, require_auth
from web.schemas import TrendAnalysisResponse

router = APIRouter(prefix="/kline", tags=["kline"])
arbitrage_router = APIRouter(prefix="/arbitrage", tags=["arbitrage"])
trends_router = APIRouter(prefix="/trends", tags=["trends"])


def _normalize_kline(raw: list) -> list[dict[str, Any]]:
    """把 SteamDT K 线数据规范化为前端 ECharts 期望的 OHLC 结构.

    SteamDT 数组格式: [timestamp, open, close, high, low]
    对象格式: {timestamp, open, high, low, close, volume}。
    注意: SteamDT K 线 API 不包含成交量数据。
    强制按 timestamp 升序排序。
    """
    out: list[dict[str, Any]] = []
    for it in raw or []:
        if isinstance(it, list) and len(it) >= 5:
            ts, o, c, h, l = it[0], it[1], it[2], it[3], it[4]
            v = it[5] if len(it) > 5 else None
        elif isinstance(it, dict):
            ts = it.get("timestamp") or it.get("time") or it.get("t")
            o = it.get("open") or it.get("o")
            h = it.get("high") or it.get("h")
            l = it.get("low") or it.get("l")
            c = it.get("close") or it.get("c")
            v = it.get("volume") or it.get("v")
        else:
            continue
        try:
            out.append({
                "timestamp": int(ts),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(v) if v is not None else None,
            })
        except (TypeError, ValueError):
            continue
    # 强制按 timestamp 升序，避免依赖服务端顺序
    out.sort(key=lambda x: x["timestamp"])
    return out


@router.get("/{market_hash_name}")
def get_kline(
    market_hash_name: str,
    period: int = 2,
    count: int = 30,
    platform: str = "ALL",
    request: Request = None,  # type: ignore[assignment]
    user: dict = Depends(require_auth),
) -> dict[str, Any]:
    """查询饰品 K 线数据.

    参数:
        period: 1=时K, 2=日K, 3=周K
        count: 返回条数
        platform: 平台过滤，默认 ALL
    """
    client = request.app.state.steamdt_client
    try:
        resp = client.get_item_kline(
            market_hash_name=market_hash_name,
            kline_type=period,
            platform=platform,
        )
    except SteamDTRateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail={"retry_after": int(e.retry_after) + 1},
        )
    except SteamDTBusinessError as e:
        raise HTTPException(
            status_code=502,
            detail=f"[{e.code}] {e.error_msg}",
        )
    except SteamDTError as e:
        raise HTTPException(status_code=502, detail=str(e))

    raw = resp.get("data") or []
    series = _normalize_kline(raw)
    if count > 0:
        series = series[-count:]

    return {
        "market_hash_name": market_hash_name,
        "period": period,
        "data": series,
    }


# ------------------------------------------------------------------
# Arbitrage（跨平台价差）
# ------------------------------------------------------------------
@arbitrage_router.get("", response_model=list[dict[str, Any]])
def get_arbitrage(
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> list[dict[str, Any]]:
    """获取所有监控品的跨平台价差."""
    latest = db.get_latest_prices()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in latest:
        name = item["market_hash_name"]
        grouped.setdefault(name, []).append(item)

    results: list[dict[str, Any]] = []
    for name, platforms in grouped.items():
        if len(platforms) < 2:
            continue
        prices = [p["price"] for p in platforms]
        min_price = min(prices)
        max_price = max(prices)
        min_platform = next(p["platform"] for p in platforms if p["price"] == min_price)
        max_platform = next(p["platform"] for p in platforms if p["price"] == max_price)
        spread = max_price - min_price
        spread_percent = ((spread / min_price) * 100) if min_price > 0 else 0.0
        results.append({
            "market_hash_name": name,
            "min_price": min_price,
            "min_platform": min_platform,
            "max_price": max_price,
            "max_platform": max_platform,
            "spread": spread,
            "spread_percent": round(spread_percent, 2),
            "platforms": platforms,
        })

    # 按价差百分比降序排列
    results.sort(key=lambda x: x["spread_percent"], reverse=True)
    return results


@arbitrage_router.get("/{market_hash_name}")
def get_arbitrage_item(
    market_hash_name: str,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict[str, Any]:
    """获取指定饰品的各平台价差明细."""
    platforms = db.get_price_by_platforms(market_hash_name)
    if len(platforms) < 2:
        return {
            "market_hash_name": market_hash_name,
            "spread": 0.0,
            "spread_percent": 0.0,
            "platforms": platforms,
        }

    prices = [p["price"] for p in platforms]
    min_price = min(prices)
    max_price = max(prices)
    spread = max_price - min_price
    spread_percent = ((spread / min_price) * 100) if min_price > 0 else 0.0

    return {
        "market_hash_name": market_hash_name,
        "min_price": min_price,
        "max_price": max_price,
        "spread": spread,
        "spread_percent": round(spread_percent, 2),
        "platforms": platforms,
    }


# ------------------------------------------------------------------
# Trends（趋势分析）
# ------------------------------------------------------------------
@trends_router.get("/{market_hash_name}", response_model=TrendAnalysisResponse)
def get_trends(
    market_hash_name: str,
    days: int = 30,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict[str, Any]:
    """获取指定饰品的趋势分析.

    参数:
        days: 分析最近 N 天的数据（默认 30）.
    """
    analyzer = TrendAnalyzer(db)
    result = analyzer.analyze(market_hash_name, days)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"{market_hash_name} 历史数据不足，无法分析趋势",
        )
    return result
