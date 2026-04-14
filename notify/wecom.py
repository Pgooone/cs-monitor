"""企业微信机器人通知渠道."""

import httpx
from loguru import logger

from notify.base import NotificationChannel


class WeComChannel(NotificationChannel):
    """企业微信机器人 Webhook 渠道."""

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send(self, title: str, content: str) -> bool:
        """发送企业微信文本通知."""
        payload = {
            "msgtype": "text",
            "text": {"content": f"{title}\n\n{content}"},
        }
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if data.get("errcode") == 0:
                    logger.debug("企微通知发送成功")
                    return True
                logger.error(f"企微通知发送失败: {data}")
                return False
        except Exception as e:
            logger.error(f"企微通知请求异常: {e}")
            return False
