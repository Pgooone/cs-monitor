"""通知渠道基类."""

from abc import ABC, abstractmethod

from loguru import logger


class NotificationChannel(ABC):
    """通知渠道抽象基类."""

    @abstractmethod
    def send(self, title: str, content: str) -> bool:
        """发送通知.

        Args:
            title: 通知标题.
            content: 通知正文.

        Returns:
            是否发送成功.
        """
        ...

    def send_with_retry(
        self,
        title: str,
        content: str,
        max_retries: int = 3,
    ) -> bool:
        """带重试的通知发送."""
        for attempt in range(1, max_retries + 1):
            try:
                if self.send(title, content):
                    return True
            except Exception as e:
                logger.warning(
                    f"通知发送异常 (尝试 {attempt}/{max_retries}): {e}"
                )
            if attempt < max_retries:
                import time

                time.sleep(1)
        logger.error(f"通知发送失败，已重试 {max_retries} 次")
        return False
