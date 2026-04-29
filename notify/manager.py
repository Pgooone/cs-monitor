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
        display_name = alert.get("display_name") or market_hash_name
        alert_type = alert["alert_type"]
        current_price = alert["current_price"]
        baseline_price = alert["baseline_price"]
        change_percent = alert["change_percent"]

        if alert_type == "price_surge":
            direction = "📈 涨价"
            emoji = "🔴"
        elif alert_type == "price_drop":
            direction = "📉 跌价"
            emoji = "🟢"
        else:
            direction = "价格变动"
            emoji = "⚪"

        title = f"{emoji} CS2 饰品价格波动提醒 - {direction}"
        content = (
            f"📦 饰品：{display_name}\n"
            f"💰 当前价格：¥{current_price:.2f}\n"
            f"📊 前日收盘：¥{baseline_price:.2f}\n"
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

        display_name = alert.get("display_name") or market_hash_name
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

        # 方向指标
        price_up = price_change > 0
        qty_up = quantity_change > 0
        price_emoji = "🔺" if price_up else "🔻" if price_change < 0 else "➖"
        qty_emoji = "🔺" if qty_up else "🔻" if quantity_change < 0 else "➖"

        if alert_type == "both":
            title = "🎯 [极致追踪] 价格 & 数量同时变动"
            # 根据量价方向组合生成智能提示
            if qty_up and price_up:
                hint = "💡 量价齐升，市场热度上升，可能有利好"
            elif qty_up and not price_up:
                hint = "💡 在售量增价跌，可能有人在抛售"
            elif not qty_up and price_up:
                hint = "💡 在售量减价涨，可能有人在扫货"
            else:
                hint = "💡 量价齐跌，市场趋于冷清"

            content = (
                f"📦 饰品：{display_name}\n"
                f"🏪 平台：{platform}\n\n"
                f"💰 价格：¥{prev_price:.2f} → ¥{curr_price:.2f} "
                f"（{price_change_percent:+.2f}%）\n"
                f"📦 数量：{prev_quantity} 件 → {curr_quantity} 件 "
                f"（{quantity_change_percent:+.2f}%）\n\n"
                f"🕐 时间：{now_str}\n"
                f"{hint}"
            )
        elif alert_type == "price_change":
            direction = "上涨" if price_up else "下跌"
            title = f"🎯 [极致追踪] 价格{direction}"
            content = (
                f"📦 饰品：{display_name}\n"
                f"🏪 平台：{platform}\n"
                f"💰 当前价格：¥{curr_price:.2f}\n"
                f"💰 上次价格：¥{prev_price:.2f}\n"
                f"{price_emoji} 变动：{price_change:+.2f}（{price_change_percent:+.2f}%）\n"
                f"📊 在售数量：{curr_quantity} 件\n"
                f"🕐 时间：{now_str}"
            )
        else:  # quantity_change
            direction = "增加" if qty_up else "减少"
            title = f"🎯 [极致追踪] 在售数量{direction}"
            verb = "卖出" if qty_up else "买入"
            content = (
                f"📦 饰品：{display_name}\n"
                f"🏪 平台：{platform}\n"
                f"📊 当前在售：{curr_quantity} 件\n"
                f"📊 上次在售：{prev_quantity} 件\n"
                f"{qty_emoji} 变动：{quantity_change:+d} 件（"
                f"{quantity_change_percent:+.2f}%）\n"
                f"💰 当前价格：¥{curr_price:.2f}\n"
                f"🕐 时间：{now_str}\n"
                f"💡 在售数量{direction}，可能意味着有人在{verb}"
            )

        return self.channel.send_with_retry(title, content)
