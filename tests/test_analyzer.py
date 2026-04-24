"""Analyzer 模块单元测试."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.steamdt import SteamDTClient, SteamDTConfig
from config import MonitorConfig
from core.analyzer import PriceAnalyzer
from storage.database import Database


class TestPriceAnalyzer:
    """测试 PriceAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """创建测试用的 PriceAnalyzer."""
        config = SteamDTConfig(api_key="test-key")
        client = SteamDTClient(config)
        monitor_config = MonitorConfig(
            watchlist=[
                {"name": "AK-47 | Redline (Field-Tested)", "threshold": 5.0},
            ],
            default_threshold_percent=5.0,
            alert_cooldown_hours=4,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Database(Path(tmpdir) / "test.db")
            # 预先插入饰品
            db.insert_item("AK-47 | Redline (Field-Tested)")
            analyzer = PriceAnalyzer(client, db, monitor_config)
            # Mock notifier 避免测试依赖外部通知配置
            analyzer.notifier = MagicMock()
            analyzer.notifier.send_normal_alert = MagicMock(return_value=True)
            yield analyzer

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_analyze_price_surge(self, mock_sleep, analyzer):
        """测试涨价超过阈值时触发 price_surge 告警."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"avgPrice": 100.0},
        }
        analyzer.client._client.request = MagicMock(return_value=mock_response)

        records = [
            {"market_hash_name": "AK-47 | Redline (Field-Tested)", "platform": "BUFF", "price": 106.0},
        ]
        alerts = analyzer.analyze(records)

        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "price_surge"
        assert alerts[0]["change_percent"] == pytest.approx(6.0)

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_analyze_price_drop(self, mock_sleep, analyzer):
        """测试跌价超过阈值时触发 price_drop 告警."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"avgPrice": 100.0},
        }
        analyzer.client._client.request = MagicMock(return_value=mock_response)

        records = [
            {"market_hash_name": "AK-47 | Redline (Field-Tested)", "platform": "BUFF", "price": 94.0},
        ]
        alerts = analyzer.analyze(records)

        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "price_drop"
        assert alerts[0]["change_percent"] == pytest.approx(-6.0)

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_analyze_no_alert_within_threshold(self, mock_sleep, analyzer):
        """测试波动在阈值范围内时不触发告警."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"avgPrice": 100.0},
        }
        analyzer.client._client.request = MagicMock(return_value=mock_response)

        records = [
            {"market_hash_name": "AK-47 | Redline (Field-Tested)", "platform": "BUFF", "price": 102.0},
        ]
        alerts = analyzer.analyze(records)

        assert len(alerts) == 0

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_analyze_cooldown(self, mock_sleep, analyzer):
        """测试同一方向告警在冷却期内不会重复触发."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"avgPrice": 100.0},
        }
        analyzer.client._client.request = MagicMock(return_value=mock_response)

        records = [
            {"market_hash_name": "AK-47 | Redline (Field-Tested)", "platform": "BUFF", "price": 106.0},
        ]

        # 第一次应触发告警
        alerts1 = analyzer.analyze(records)
        assert len(alerts1) == 1

        # 第二次在冷却期内不应触发
        alerts2 = analyzer.analyze(records)
        assert len(alerts2) == 0

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_analyze_fallback_to_latest_price(self, mock_sleep, analyzer):
        """测试 7 天均价缺失时回退到上一次采集价格."""
        # 7天均价 API 失败
        analyzer.client._client.request = MagicMock(
            side_effect=Exception("API Error")
        )

        # 先写入一条历史价格记录
        analyzer.db.insert_price_record(
            "AK-47 | Redline (Field-Tested)", "BUFF", 100.0
        )

        records = [
            {"market_hash_name": "AK-47 | Redline (Field-Tested)", "platform": "BUFF", "price": 106.0},
        ]
        alerts = analyzer.analyze(records)

        assert len(alerts) == 1
        assert alerts[0]["baseline_price"] == 100.0
