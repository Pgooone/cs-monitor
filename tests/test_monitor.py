"""Monitor 模块单元测试."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.steamdt import SteamDTClient, SteamDTConfig
from config import MonitorConfig
from core.monitor import PriceMonitor
from storage.database import Database


class TestPriceMonitor:
    """测试 PriceMonitor."""

    @pytest.fixture
    def monitor(self):
        """创建测试用的 PriceMonitor."""
        config = SteamDTConfig(api_key="test-key")
        client = SteamDTClient(config)
        monitor_config = MonitorConfig(
            watchlist=[
                {"name": "AK-47 | Redline (Field-Tested)", "threshold": 5.0},
            ],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            db = Database(Path(tmpdir) / "test.db")
            db.insert_watchlist_item(
                market_hash_name="AK-47 | Redline (Field-Tested)",
                threshold_percent=5.0,
                enabled=True,
            )
            yield PriceMonitor(client, db, monitor_config)

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_collect_prices_success(self, mock_sleep, monitor):
        """测试正常采集价格并写入数据库."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "marketHashName": "AK-47 | Redline (Field-Tested)",
                    "dataList": [
                        {"platform": "BUFF", "sellPrice": 125.0, "sellCount": 42},
                        {"platform": "UUYP", "sellPrice": 124.5, "sellCount": 38},
                    ],
                },
            ],
        }
        monitor.client._client.request = MagicMock(return_value=mock_response)

        records = monitor.collect_prices()

        assert len(records) == 2
        assert records[0]["platform"] == "BUFF"
        assert records[0]["price"] == 125.0

        # 验证数据库写入
        latest = monitor.db.get_latest_price(
            "AK-47 | Redline (Field-Tested)", "BUFF"
        )
        assert latest is not None
        assert latest["price"] == 125.0

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_collect_prices_empty_watchlist(self, mock_sleep, monitor):
        """测试空监控清单."""
        with monitor.db._cursor() as cursor:
            cursor.execute("DELETE FROM watchlist")
        records = monitor.collect_prices()
        assert records == []

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_collect_prices_api_failure(self, mock_sleep, monitor):
        """测试 API 失败时返回空列表."""
        monitor.client._client.request = MagicMock(
            side_effect=Exception("API Error")
        )
        records = monitor.collect_prices()
        assert records == []

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_collect_prices_api_not_success(self, mock_sleep, monitor):
        """测试 API 返回 success=False 时返回空列表."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "errorMsg": "参数错误",
        }
        monitor.client._client.request = MagicMock(return_value=mock_response)
        records = monitor.collect_prices()
        assert records == []
