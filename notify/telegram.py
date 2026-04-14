"""Telegram Bot 通知渠道."""

import httpx
from loguru import logger

from notify.base import NotificationChannel


class TelegramChannel(NotificationChannel):
    """Telegram Bot 通知渠道."""

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send(self, title: str, content: str) -> bool:
        """发送 Telegram 文本通知."""
        payload = {
            "chat_id": self.chat_id,
            "text": f"{title}\n\n{content}",
            "parse_mode": "HTML",
        }
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(self.api_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if data.get("ok"):
                    logger.debug("Telegram 通知发送成功")
                    return True
                logger.error(f"Telegram 通知发送失败: {data}")
                return False
        except Exception as e:
            logger.error(f"Telegram 通知请求异常: {e}")
            return False
