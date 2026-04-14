"""API 模块单元测试."""

from unittest.mock import MagicMock, patch

import pytest

from api.steamdt import SteamDTAPIError, SteamDTClient, SteamDTConfig


class TestSteamDTClient:
    """测试 SteamDTClient."""

    @pytest.fixture
    def client(self):
        """创建测试客户端."""
        config = SteamDTConfig(api_key="test-key")
        return SteamDTClient(config)

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_get_items_batch_success(self, mock_sleep, client):
        """测试批量查询成功."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "marketHashName": "AK-47 | Redline (Field-Tested)",
                    "dataList": [
                        {"platform": "BUFF", "sellPrice": 125.0, "sellCount": 42},
                    ],
                },
            ],
            "errorCode": 0,
            "errorMsg": "",
        }
        client._client.request = MagicMock(return_value=mock_response)

        result = client.get_items_batch(["AK-47 | Redline (Field-Tested)"])

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["marketHashName"] == "AK-47 | Redline (Field-Tested)"

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_get_items_batch_empty(self, mock_sleep, client):
        """测试空列表返回空数据."""
        result = client.get_items_batch([])
        assert result["data"] == []

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_get_items_batch_too_many(self, mock_sleep, client):
        """测试超过 100 个抛出异常."""
        with pytest.raises(ValueError, match="最多支持 100 个"):
            client.get_items_batch(["item"] * 101)

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_get_7day_average_success(self, mock_sleep, client):
        """测试 7 天均价查询成功."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "marketHashName": "AK-47 | Redline (Field-Tested)",
                "avgPrice": 120.0,
                "dataList": [
                    {"platform": "BUFF", "avgPrice": 118.0},
                ],
            },
            "errorCode": 0,
            "errorMsg": "",
        }
        client._client.request = MagicMock(return_value=mock_response)

        result = client.get_7day_average("AK-47 | Redline (Field-Tested)")

        assert result["success"] is True
        assert result["data"]["avgPrice"] == 120.0

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_get_all_items_success(self, mock_sleep, client):
        """测试获取饰品基础信息成功."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"name": "AK-47", "marketHashName": "AK-47 | Redline (Field-Tested)"},
            ],
            "errorCode": 0,
            "errorMsg": "",
        }
        client._client.request = MagicMock(return_value=mock_response)

        result = client.get_all_items()

        assert result["success"] is True
        assert len(result["data"]) == 1

    @patch("api.steamdt.time.sleep", return_value=None)
    def test_request_retry_then_fail(self, mock_sleep, client):
        """测试重试后仍失败抛出异常."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        error = httpx.HTTPStatusError(
            "Server error",
            request=MagicMock(),
            response=mock_response,
        )
        mock_response.raise_for_status.side_effect = error

        client._client.request = MagicMock(return_value=mock_response)

        with pytest.raises(SteamDTAPIError):
            client.get_all_items()

        # 默认重试 3 次
        assert client._client.request.call_count == 3
