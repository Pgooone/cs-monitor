"""Notify 模块单元测试."""

from unittest.mock import MagicMock, patch

import pytest

from config import MonitorConfig
from notify.manager import NotificationManager
from notify.serverchan import ServerChanChannel
from notify.telegram import TelegramChannel
from notify.wecom import WeComChannel


class TestWeComChannel:
    """测试 WeComChannel."""

    @patch("notify.wecom.httpx.Client")
    def test_send_success(self, mock_client_class):
        """测试企微发送成功."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_class.return_value = mock_client

        channel = WeComChannel("https://qyapi.weixin.qq.com/test")
        assert channel.send("标题", "内容") is True

    @patch("notify.wecom.httpx.Client")
    def test_send_failure(self, mock_client_class):
        """测试企微发送失败返回 False."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"errcode": 40001, "errmsg": "invalid"}
        mock_resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_class.return_value = mock_client

        channel = WeComChannel("https://qyapi.weixin.qq.com/test")
        assert channel.send("标题", "内容") is False


class TestTelegramChannel:
    """测试 TelegramChannel."""

    @patch("notify.telegram.httpx.Client")
    def test_send_success(self, mock_client_class):
        """测试 Telegram 发送成功."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        mock_resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_class.return_value = mock_client

        channel = TelegramChannel("token123", "chat456")
        assert channel.send("标题", "内容") is True


class TestServerChanChannel:
    """测试 ServerChanChannel."""

    @patch("notify.serverchan.httpx.Client")
    def test_send_success(self, mock_client_class):
        """测试 Server 酱发送成功."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": 0, "message": "success"}
        mock_resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_class.return_value = mock_client

        channel = ServerChanChannel("SENDKEY123")
        assert channel.send("标题", "内容") is True


class TestNotificationManager:
    """测试 NotificationManager."""

    def test_create_wecom_channel(self):
        """测试根据配置创建企微渠道."""
        config = MonitorConfig(
            notify_channel="wecom",
            wecom_webhook_url="https://qyapi.weixin.qq.com/test",
        )
        manager = NotificationManager(config)
        assert isinstance(manager.channel, WeComChannel)

    def test_create_no_channel(self):
        """测试未配置有效渠道时 channel 为 None."""
        config = MonitorConfig(
            notify_channel="wecom",
            wecom_webhook_url="",
        )
        manager = NotificationManager(config)
        assert manager.channel is None

    @patch.object(WeComChannel, "send_with_retry", return_value=True)
    def test_send_normal_alert(self, mock_send):
        """测试普通监控告警格式化发送."""
        config = MonitorConfig(
            notify_channel="wecom",
            wecom_webhook_url="https://qyapi.weixin.qq.com/test",
        )
        manager = NotificationManager(config)
        alert = {
            "market_hash_name": "AK-47 | Redline (Field-Tested)",
            "alert_type": "price_surge",
            "current_price": 130.0,
            "baseline_price": 120.0,
            "change_percent": 8.33,
        }
        assert manager.send_normal_alert(alert) is True
        args = mock_send.call_args[0]
        assert "CS2 饰品价格波动提醒" in args[0]
        assert "AK-47 | Redline (Field-Tested)" in args[1]

    @patch.object(WeComChannel, "send_with_retry", return_value=True)
    def test_send_extreme_alert_both(self, mock_send):
        """测试极致追踪合并告警格式化发送."""
        config = MonitorConfig(
            notify_channel="wecom",
            wecom_webhook_url="https://qyapi.weixin.qq.com/test",
        )
        manager = NotificationManager(config)
        alert = {
            "alert_type": "both",
            "prev_price": 125.0,
            "curr_price": 128.5,
            "price_change": 3.5,
            "price_change_percent": 2.8,
            "prev_quantity": 42,
            "curr_quantity": 38,
            "quantity_change": -4,
            "quantity_change_percent": -9.52,
        }
        assert (
            manager.send_extreme_alert(
                alert,
                "AK-47 | Redline (Field-Tested)",
                "BUFF",
            )
            is True
        )
        args = mock_send.call_args[0]
        assert "价格 & 数量同时变动" in args[0]
        assert "125.00" in args[1]
