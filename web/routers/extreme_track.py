"""极致追踪路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from storage.database import Database
from web.deps import get_db, require_auth
from web.schemas import (
    ExtremeTrackConfig,
    ExtremeTrackConfigCreate,
    ExtremeTrackConfigUpdate,
)

router = APIRouter(prefix="/extreme-track", tags=["extreme-track"])


@router.get("", response_model=list[ExtremeTrackConfig])
def get_extreme_track_configs(
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> list[dict]:
    """获取全部极致追踪配置."""
    return db.get_extreme_track_configs(enabled_only=False)


@router.post("", response_model=ExtremeTrackConfig)
def create_extreme_track_config(
    item: ExtremeTrackConfigCreate,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """添加极致追踪配置."""
    existing = db.get_extreme_track_config(
        item.market_hash_name, item.platform
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"'{item.market_hash_name}@{item.platform}' 的极致追踪配置已存在",
        )
    db.insert_extreme_track_config(
        market_hash_name=item.market_hash_name,
        platform=item.platform,
        interval_seconds=item.interval_seconds,
        enabled=item.enabled,
        price_track_enabled=item.price_track_enabled,
        price_change_mode=item.price_change_mode,
        price_threshold_percent=item.price_threshold_percent,
        quantity_track_enabled=item.quantity_track_enabled,
        quantity_change_mode=item.quantity_change_mode,
        quantity_threshold_percent=item.quantity_threshold_percent,
        alert_cooldown_seconds=item.alert_cooldown_seconds,
        quiet_hours_start=item.quiet_hours_start,
        quiet_hours_end=item.quiet_hours_end,
    )
    result = db.get_extreme_track_config(
        item.market_hash_name, item.platform
    )
    if not result:
        raise HTTPException(status_code=500, detail="创建失败")
    return dict(result)


@router.put("/{market_hash_name}/{platform}", response_model=ExtremeTrackConfig)
def update_extreme_track_config(
    market_hash_name: str,
    platform: str,
    item: ExtremeTrackConfigUpdate,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """更新极致追踪配置."""
    existing = db.get_extreme_track_config(market_hash_name, platform)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"'{market_hash_name}@{platform}' 不存在",
        )
    update_fields: dict = {}
    if item.interval_seconds is not None:
        update_fields["interval_seconds"] = item.interval_seconds
    if item.enabled is not None:
        update_fields["enabled"] = item.enabled
    if item.price_track_enabled is not None:
        update_fields["price_track_enabled"] = item.price_track_enabled
    if item.price_change_mode is not None:
        update_fields["price_change_mode"] = item.price_change_mode
    if item.price_threshold_percent is not None:
        update_fields["price_threshold_percent"] = item.price_threshold_percent
    if item.quantity_track_enabled is not None:
        update_fields["quantity_track_enabled"] = item.quantity_track_enabled
    if item.quantity_change_mode is not None:
        update_fields["quantity_change_mode"] = item.quantity_change_mode
    if item.quantity_threshold_percent is not None:
        update_fields["quantity_threshold_percent"] = item.quantity_threshold_percent
    if item.alert_cooldown_seconds is not None:
        update_fields["alert_cooldown_seconds"] = item.alert_cooldown_seconds
    if item.quiet_hours_start is not None:
        update_fields["quiet_hours_start"] = item.quiet_hours_start
    if item.quiet_hours_end is not None:
        update_fields["quiet_hours_end"] = item.quiet_hours_end

    db.update_extreme_track_config(
        market_hash_name, platform, **update_fields
    )
    result = db.get_extreme_track_config(market_hash_name, platform)
    return dict(result)


@router.delete("/{market_hash_name}/{platform}")
def delete_extreme_track_config(
    market_hash_name: str,
    platform: str,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """删除极致追踪配置."""
    existing = db.get_extreme_track_config(market_hash_name, platform)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"'{market_hash_name}@{platform}' 不存在",
        )
    db.delete_extreme_track_config(market_hash_name, platform)
    return {"message": f"已删除 '{market_hash_name}@{platform}'"}


@router.post("/{market_hash_name}/{platform}/toggle")
def toggle_extreme_track_config(
    market_hash_name: str,
    platform: str,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """切换极致追踪配置启停状态."""
    existing = db.get_extreme_track_config(market_hash_name, platform)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"'{market_hash_name}@{platform}' 不存在",
        )
    new_enabled = not bool(existing["enabled"])
    db.update_extreme_track_config(
        market_hash_name, platform, enabled=new_enabled
    )
    return {
        "market_hash_name": market_hash_name,
        "platform": platform,
        "enabled": new_enabled,
    }
