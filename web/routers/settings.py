"""系统设置路由."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from notify.wecom import WeComChannel
from storage.database import Database
from web.deps import get_config, get_db, require_auth
from web.schemas import NotifySettings, NotifyTestRequest

router = APIRouter(prefix="/settings", tags=["settings"])


# 配置键名映射
CONFIG_KEYS = {
    "notify_channel": "notify_channel",
    "wecom_webhook_url": "wecom_webhook_url",
    "telegram_bot_token": "telegram_bot_token",
    "telegram_chat_id": "telegram_chat_id",
    "serverchan_sendkey": "serverchan_sendkey",
}


@router.get("/notify", response_model=NotifySettings)
def get_notify_settings(
    db: Database = Depends(get_db),
    config=Depends(get_config),
    user: dict = Depends(require_auth),
) -> dict:
    """获取当前通知配置（DB 优先，fallback 到 .env/config）."""
    return {
        "notify_channel": db.get_system_config("notify_channel") or config.notify_channel,
        "wecom_webhook_url": db.get_system_config("wecom_webhook_url") or config.wecom_webhook_url,
        "telegram_bot_token": db.get_system_config("telegram_bot_token") or config.telegram_bot_token,
        "telegram_chat_id": db.get_system_config("telegram_chat_id") or config.telegram_chat_id,
        "serverchan_sendkey": db.get_system_config("serverchan_sendkey") or config.serverchan_sendkey,
    }


@router.put("/notify")
def update_notify_settings(
    settings: NotifySettings,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """更新通知配置到 system_config 表."""
    for field in CONFIG_KEYS:
        value = getattr(settings, field)
        if value is not None:
            db.set_system_config(field, str(value))
    return {"message": "通知配置已更新"}


@router.post("/notify/test")
def test_notify(
    req: NotifyTestRequest,
    db: Database = Depends(get_db),
    config=Depends(get_config),
    user: dict = Depends(require_auth),
) -> dict:
    """发送测试通知."""
    channel = req.channel or (
        db.get_system_config("notify_channel") or config.notify_channel
    )

    if channel == "wecom":
        url = req.extra.get("webhook_url") if req.extra else None
        if not url:
            url = db.get_system_config("wecom_webhook_url") or config.wecom_webhook_url
        if not url:
            raise HTTPException(status_code=400, detail="企业微信 Webhook URL 未配置")
        ch = WeComChannel(webhook_url=url)
        ok = ch.send_with_retry(
            "CS2 Monitor 测试通知",
            "这是一条来自 CS2 饰品监控系统的测试消息。",
        )
        if not ok:
            raise HTTPException(status_code=500, detail="企业微信通知发送失败")
        return {"message": "测试通知已发送"}

    # Telegram / ServerChan 暂未实现前端测试，预留接口
    raise HTTPException(status_code=400, detail=f"渠道 '{channel}' 暂不支持测试")


@router.get("/system")
def get_system_info(
    db: Database = Depends(get_db),
    config=Depends(get_config),
    user: dict = Depends(require_auth),
) -> dict:
    """获取系统信息（数据目录、版本、数据库状态等）."""
    db_path = Path(config.db_path)
    db_size = db_path.stat().st_size if db_path.exists() else 0
    return {
        "version": "1.0.0",
        "db_path": str(db_path),
        "db_size": db_size,
        "db_size_human": _human_readable_size(db_size),
        "data_dir": str(db_path.parent),
        "watchlist_count": db.get_watchlist_count(enabled_only=False),
        "extreme_track_count": db.get_extreme_track_count(enabled_only=False),
    }


@router.get("/db/export")
def export_database(
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> FileResponse:
    """导出数据库文件."""
    db_path = Path(db.db_path)
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="数据库文件不存在")
    return FileResponse(
        path=str(db_path),
        filename="cs_monitor.db",
        media_type="application/octet-stream",
    )


@router.post("/db/clear")
def clear_database(
    confirm: bool = False,
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict:
    """清空价格记录和告警记录（保留配置表）."""
    if not confirm:
        raise HTTPException(status_code=400, detail="必须设置 confirm=true 才能清空数据")
    try:
        with db._cursor() as cursor:
            cursor.execute("DELETE FROM price_records")
            cursor.execute("DELETE FROM alert_logs")
            cursor.execute("DELETE FROM extreme_track_snapshots")
            cursor.execute("DELETE FROM extreme_track_alerts")
            cursor.execute("DELETE FROM archived_prices")
        return {
            "message": "数据已清空",
            "cleared_tables": [
                "price_records",
                "alert_logs",
                "extreme_track_snapshots",
                "extreme_track_alerts",
                "archived_prices",
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空失败: {e}")


def _human_readable_size(size_bytes: int) -> str:
    """将字节数转换为人类可读格式."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    import math
    idx = int(math.floor(math.log(size_bytes, 1024)))
    idx = min(idx, len(units) - 1)
    size = round(size_bytes / (1024 ** idx), 2)
    return f"{size} {units[idx]}"
