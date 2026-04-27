"""Analyzer 模块单元测试."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.steamdt import (
    SteamDTBusinessError,
    SteamDTClient,
    SteamDTConfig,
    SteamDTError,
    SteamDTRateLimitError,
)
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
            "data": {"dataList": [{"avgPrice": 100.0}]},
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
            "data": {"dataList": [{"avgPrice": 100.0}]},
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
            "data": {"dataList": [{"avgPrice": 100.0}]},
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
            "data": {"dataList": [{"avgPrice": 100.0}]},
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

    def test_analyze_fallback_to_latest_price(self, analyzer):
        """测试 7 天均价 API 失败时回退到上一次采集价格."""
        # 7天均价 API 抛出 SteamDTError（网络层错误已被 _request 包装）
        analyzer.client.get_7day_average = MagicMock(
            side_effect=SteamDTError("network error")
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

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_baseline_cache_hit(self, mock_sleep, analyzer):
        """测试 6h 缓存命中时不再调用 API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"dataList": [{"avgPrice": 100.0}]},
        }
        analyzer.client._client.request = MagicMock(return_value=mock_response)

        name = "AK-47 | Redline (Field-Tested)"
        # 第一次调用 → 调 API
        price1 = analyzer._get_baseline_price(name)
        assert price1 == 100.0
        assert analyzer.client._client.request.call_count == 1

        # 第二次调用 → 命中缓存，不调 API
        price2 = analyzer._get_baseline_price(name)
        assert price2 == 100.0
        assert analyzer.client._client.request.call_count == 1  # 未增加

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_baseline_cache_expired(self, mock_sleep, analyzer):
        """测试缓存过期后重新调用 API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"dataList": [{"avgPrice": 100.0}]},
        }
        analyzer.client._client.request = MagicMock(return_value=mock_response)

        name = "AK-47 | Redline (Field-Tested)"
        analyzer._get_baseline_price(name)
        assert analyzer.client._client.request.call_count == 1

        # 模拟缓存过期（手动将时间戳改到 7 小时前）
        analyzer._avg_cache[name] = (
            100.0,
            datetime.utcnow() - timedelta(hours=7),
        )

        analyzer._get_baseline_price(name)
        assert analyzer.client._client.request.call_count == 2  # 重新调 API

    def test_baseline_rate_limit_fallback_to_db(self, analyzer):
        """测试 SteamDTRateLimitError 时 fallback 到 DB 最新价."""
        analyzer.client.get_7day_average = MagicMock(
            side_effect=SteamDTRateLimitError(retry_after=60.0)
        )
        analyzer.db.insert_price_record(
            "AK-47 | Redline (Field-Tested)", "BUFF", 99.0
        )

        price = analyzer._get_baseline_price("AK-47 | Redline (Field-Tested)")
        assert price == 99.0

    def test_baseline_business_error_fallback_to_db(self, analyzer):
        """测试 SteamDTBusinessError 时 fallback 到 DB 最新价."""
        analyzer.client.get_7day_average = MagicMock(
            side_effect=SteamDTBusinessError(code=4001, message="参数错误")
        )
        analyzer.db.insert_price_record(
            "AK-47 | Redline (Field-Tested)", "BUFF", 88.0
        )

        price = analyzer._get_baseline_price("AK-47 | Redline (Field-Tested)")
        assert price == 88.0

    def test_baseline_generic_error_fallback_to_db(self, analyzer):
        """测试 SteamDTError 时 fallback 到 DB 最新价."""
        analyzer.client.get_7day_average = MagicMock(
            side_effect=SteamDTError("network error")
        )
        analyzer.db.insert_price_record(
            "AK-47 | Redline (Field-Tested)", "BUFF", 77.0
        )

        price = analyzer._get_baseline_price("AK-47 | Redline (Field-Tested)")
        assert price == 77.0

    def test_baseline_success_false_fallback_to_db(self, analyzer):
        """测试 API 返回 success=false 时 fallback 到 DB."""
        analyzer.client.get_7day_average = MagicMock(
            return_value={"success": False, "errorCode": 4001, "errorMsg": "参数错误"}
        )
        analyzer.db.insert_price_record(
            "AK-47 | Redline (Field-Tested)", "BUFF", 66.0
        )

        price = analyzer._get_baseline_price("AK-47 | Redline (Field-Tested)")
        assert price == 66.0
