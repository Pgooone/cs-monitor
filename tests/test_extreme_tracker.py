"""ExtremeTracker 模块单元测试."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.steamdt import (
    SteamDTClient,
    SteamDTConfig,
    SteamDTRateLimitError,
)
from config import MonitorConfig
from core.extreme_tracker import ExtremeTracker
from storage.database import Database


class TestExtremeTracker:
    """测试 ExtremeTracker."""

    @pytest.fixture
    def tracker(self):
        """创建测试用的 ExtremeTracker."""
        config = SteamDTConfig(api_key="test-key")
        client = SteamDTClient(config)
        monitor_config = MonitorConfig(
            extreme_track_list=[
                {
                    "market_hash_name": "AK-47 | Redline (Field-Tested)",
                    "platform": "BUFF",
                    "interval_seconds": 60,
                    "price_track_enabled": True,
                    "price_change_mode": "any",
                    "quantity_track_enabled": True,
                    "quantity_change_mode": "any",
                    "alert_cooldown_seconds": 0,
                },
            ],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Database(Path(tmpdir) / "test.db")
            db.insert_extreme_track_config(
                market_hash_name="AK-47 | Redline (Field-Tested)",
                platform="BUFF",
                interval_seconds=60,
                price_track_enabled=True,
                price_change_mode="any",
                quantity_track_enabled=True,
                quantity_change_mode="any",
                alert_cooldown_seconds=0,
            )
            tracker = ExtremeTracker(client, db, monitor_config)
            # Mock notifier 避免测试依赖外部通知配置
            tracker.notifier = MagicMock()
            tracker.notifier.send_extreme_alert = MagicMock(return_value=True)
            yield tracker

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_tick_first_run_no_alert(self, mock_sleep, tracker):
        """测试首次运行只记录快照，不告警."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 125.0, "sellCount": 42},
            ],
        }
        tracker.client._client.request = MagicMock(return_value=mock_response)

        results = tracker.tick()
        assert len(results) == 0

        # 验证快照已写入
        snapshot = tracker.db.get_latest_snapshot(
            "AK-47 | Redline (Field-Tested)", "BUFF"
        )
        assert snapshot is not None
        assert snapshot["price"] == 125.0
        assert snapshot["quantity"] == 42

    @patch("api.steamdt.time.sleep", return_value=None)
    @patch("core.extreme_tracker.time.time")
    def test_tick_price_change_alert(self, mock_time, mock_sleep, tracker):
        """测试价格变动触发告警."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 125.0, "sellCount": 42},
            ],
        }
        tracker.client._client.request = MagicMock(return_value=mock_response)

        # 首次采集
        mock_time.return_value = 1000
        tracker.tick()

        # 修改价格后再次采集（时间前进超过间隔）
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 130.0, "sellCount": 42},
            ],
        }
        mock_time.return_value = 1100
        results = tracker.tick()

        assert len(results) == 1
        assert results[0]["alert_type"] == "price_change"
        assert results[0]["price_change"] == 5.0

    @patch("api.steamdt.time.sleep", return_value=None)
    @patch("core.extreme_tracker.time.time")
    def test_tick_both_change_alert(self, mock_time, mock_sleep, tracker):
        """测试价格和数量同时变动触发合并告警."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 125.0, "sellCount": 42},
            ],
        }
        tracker.client._client.request = MagicMock(return_value=mock_response)

        mock_time.return_value = 1000
        tracker.tick()

        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 130.0, "sellCount": 38},
            ],
        }
        mock_time.return_value = 1100
        results = tracker.tick()

        assert len(results) == 1
        assert results[0]["alert_type"] == "both"
        assert results[0]["price_change"] == 5.0
        assert results[0]["quantity_change"] == -4

    @patch("api.steamdt.time.sleep", return_value=None)
    @patch("core.extreme_tracker.time.time")
    def test_tick_cooldown(self, mock_time, mock_sleep, tracker):
        """测试告警冷却期内不重复触发."""
        tracker.db.update_extreme_track_config(
            "AK-47 | Redline (Field-Tested)", "BUFF",
            alert_cooldown_seconds=3600,
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 125.0, "sellCount": 42},
            ],
        }
        tracker.client._client.request = MagicMock(return_value=mock_response)

        mock_time.return_value = 1000
        tracker.tick()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 130.0, "sellCount": 42},
            ],
        }
        mock_time.return_value = 1100
        results1 = tracker.tick()
        assert len(results1) == 1

        # 再次变动，应在冷却期内
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"platform": "BUFF", "sellPrice": 135.0, "sellCount": 42},
            ],
        }
        mock_time.return_value = 1200
        results2 = tracker.tick()
        assert len(results2) == 0

    @patch("core.extreme_tracker.time.sleep", return_value=None)
    def test_tick_429_rate_limit(self, mock_sleep, tracker):
        """测试 429 限流：捕获 SteamDTRateLimitError，sleep 后返回 None."""
        tracker.client._request = MagicMock(
            side_effect=SteamDTRateLimitError(retry_after=30.0, source="http")
        )

        results = tracker.tick()
        assert len(results) == 0
        mock_sleep.assert_called_once_with(30.0)

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_tick_disabled(self, mock_sleep, tracker):
        """测试禁用的追踪项不执行."""
        tracker.db.update_extreme_track_config(
            "AK-47 | Redline (Field-Tested)", "BUFF",
            enabled=False,
        )
        results = tracker.tick()
        assert len(results) == 0

    def test_is_quiet_hours(self, tracker):
        """测试免打扰时段判断."""
        from datetime import datetime
        from unittest.mock import patch as mock_patch

        config = {"quiet_hours_start": "02:00", "quiet_hours_end": "08:00"}
        with mock_patch("core.extreme_tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 15, 5, 0, 0)
            mock_dt.strptime = datetime.strptime
            assert tracker._is_quiet_hours(config) is True

        with mock_patch("core.extreme_tracker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 15, 10, 0, 0)
            mock_dt.strptime = datetime.strptime
            assert tracker._is_quiet_hours(config) is False
