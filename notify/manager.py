"""通知管理器."""

from datetime import datetime
from typing import Any

from loguru import logger

from config import MonitorConfig
from notify.base import NotificationChannel
from notify.serverchan import ServerChanChannel
from notify.telegram import TelegramChannel
from notify.wecom import WeComChannel


class NotificationManager:
    """通知管理器：负责消息格式化和渠道路由."""

    def __init__(self, config: MonitorConfig) -> None:
        self.config = config
        self.channel = self._create_channel()

    def _create_channel(self) -> NotificationChannel | None:
        """根据配置创建通知渠道."""
        channel_name = self.config.notify_channel
        if channel_name == "wecom" and self.config.wecom_webhook_url:
            return WeComChannel(self.config.wecom_webhook_url)
        elif (
            channel_name == "telegram"
            and self.config.telegram_bot_token
            and self.config.telegram_chat_id
        ):
            return TelegramChannel(
                self.config.telegram_bot_token,
                self.config.telegram_chat_id,
                proxy=self.config.telegram_proxy or None,
            )
        elif (
            channel_name == "serverchan" and self.config.serverchan_sendkey
        ):
            return ServerChanChannel(self.config.serverchan_sendkey)
        logger.warning(f"未配置有效的通知渠道: {channel_name}")
        return None

    def send_normal_alert(self, alert: dict[str, Any]) -> bool:
        """发送普通监控告警."""
        if not self.channel:
            return False

        market_hash_name = alert["market_hash_name"]
        alert_type = alert["alert_type"]
        current_price = alert["current_price"]
        baseline_price = alert["baseline_price"]
        change_percent = alert["change_percent"]

        direction = "暴涨" if alert_type == "price_surge" else "暴跌"
        emoji = "🔴" if alert_type == "price_surge" else "🟢"

        title = f"{emoji} CS2 饰品价格波动提醒 - {direction}"
        content = (
            f"📦 饰品：{market_hash_name}\n"
            f"💰 当前价格：¥{current_price:.2f}\n"
            f"📊 7天均价：¥{baseline_price:.2f}\n"
            f"📈 波动幅度：{change_percent:+.2f}%\n"
            f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        return self.channel.send_with_retry(title, content)

    def send_extreme_alert(
        self,
        alert: dict[str, Any],
        market_hash_name: str,
        platform: str,
    ) -> bool:
        """发送极致追踪告警."""
        if not self.channel:
            return False

        alert_type = alert["alert_type"]
        prev_price = alert.get("prev_price")
        curr_price = alert.get("curr_price")
        price_change = alert.get("price_change", 0)
        price_change_percent = alert.get("price_change_percent", 0)
        prev_quantity = alert.get("prev_quantity")
        curr_quantity = alert.get("curr_quantity")
        quantity_change = alert.get("quantity_change", 0)
        quantity_change_percent = alert.get("quantity_change_percent", 0)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if alert_type == "both":
            title = "🎯 [极致追踪] 价格 & 数量同时变动！"
            content = (
                f"📦 饰品：{market_hash_name}\n"
                f"🏪 平台：{platform}\n\n"
                f"💰 价格：¥{prev_price:.2f} → ¥{curr_price:.2f} "
                f"（{price_change_percent:+.2f}%）\n"
                f"📦 数量：{prev_quantity} 件 → {curr_quantity} 件 "
                f"（{quantity_change_percent:+.2f}%）\n\n"
                f"🕐 时间：{now_str}\n"
                f"💡 量跌价涨，市场可能在抢货"
            )
        elif alert_type == "price_change":
            title = "🎯 [极致追踪] 价格变动"
            content = (
                f"📦 饰品：{market_hash_name}\n"
                f"🏪 平台：{platform}\n"
                f"💰 当前价格：¥{curr_price:.2f}\n"
                f"💰 上次价格：¥{prev_price:.2f}\n"
                f"📈 变动：{price_change:+.2f}（{price_change_percent:+.2f}%）\n"
                f"📊 在售数量：{curr_quantity} 件\n"
                f"🕐 时间：{now_str}"
            )
        else:  # quantity_change
            title = "🎯 [极致追踪] 在售数量变动"
            content = (
                f"📦 饰品：{market_hash_name}\n"
                f"🏪 平台：{platform}\n"
                f"📉 当前在售：{curr_quantity} 件\n"
                f"📊 上次在售：{prev_quantity} 件\n"
                f"🔻 变动：{quantity_change:+d} 件（"
                f"{quantity_change_percent:+.2f}%）\n"
                f"💰 当前价格：¥{curr_price:.2f}\n"
                f"🕐 时间：{now_str}\n"
                f"💡 数量减少可能意味着有人在买入"
            )

        return self.channel.send_with_retry(title, content)
