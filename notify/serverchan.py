"""Server 酱通知渠道."""

import httpx
from loguru import logger

from notify.base import NotificationChannel


class ServerChanChannel(NotificationChannel):
    """Server 酱推送渠道."""

    def __init__(self, sendkey: str) -> None:
        self.sendkey = sendkey
        self.api_url = f"https://sctapi.ftqq.com/{sendkey}.send"

    def send(self, title: str, content: str) -> bool:
        """发送 Server 酱通知."""
        payload = {
            "title": title,
            "desp": content,
        }
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(self.api_url, data=payload)
                resp.raise_for_status()
                data = resp.json()
                if (
                    data.get("code") == 0
                    or data.get("data", {}).get("errno") == 0
                ):
                    logger.debug("Server 酱通知发送成功")
                    return True
                logger.error(f"Server 酱通知发送失败: {data}")
                return False
        except Exception as e:
            logger.error(f"Server 酱通知请求异常: {e}")
            return False
