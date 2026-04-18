"""系统设置路由."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from notify.wecom import WeComChannel
from storage.database import Database
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


def get_db(request: Request) -> Database:
    """依赖注入：数据库实例."""
    return request.app.state.db


def get_config(request: Request):
    """依赖注入：配置实例."""
    return request.app.state.config


@router.get("/notify", response_model=NotifySettings)
def get_notify_settings(
    db: Database = Depends(get_db),
    config=Depends(get_config),
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
