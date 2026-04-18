"""Web API 测试."""

import tempfile

import pytest
from fastapi.testclient import TestClient

from config import MonitorConfig
from storage.database import Database
from web.app import create_app


@pytest.fixture
def client():
    """创建 TestClient."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = Database(tmp.name)

    config = MonitorConfig(
        api_key="test_key",
        watchlist=[{"name": "Test Item", "threshold": 5.0}],
    )

    app = create_app(db, config)
    with TestClient(app) as tc:
        yield tc


class TestHealthEndpoint:
    """健康检查端点测试."""

    def test_health_check(self, client: TestClient) -> None:
        """测试 /api/health 返回 ok."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestDashboardEndpoint:
    """Dashboard 端点测试."""

    def test_dashboard_summary(self, client: TestClient) -> None:
        """测试 /api/dashboard/summary 返回概览数据."""
        response = client.get("/api/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert "active_watchlist" in data
        assert "extreme_track_count" in data
        assert "today_alert_count" in data
        assert "latest_price_count" in data
        assert data["active_watchlist"] == 0
        assert data["extreme_track_count"] == 0

    def test_cors_preflight(self, client: TestClient) -> None:
        """测试 CORS 预检请求."""
        response = client.options(
            "/api/dashboard/summary",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestWatchlistEndpoint:
    """监控清单端点测试."""

    def test_get_watchlist_empty(self, client: TestClient) -> None:
        """测试空监控清单返回空列表."""
        response = client.get("/api/watchlist")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_watchlist_item(self, client: TestClient) -> None:
        """测试创建监控清单项."""
        payload = {
            "market_hash_name": "Test Knife | Doppler (Factory New)",
            "display_name": "Test Knife",
            "threshold_percent": 3.0,
            "enabled": True,
        }
        response = client.post("/api/watchlist", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["market_hash_name"] == payload["market_hash_name"]
        assert data["display_name"] == payload["display_name"]
        assert data["threshold_percent"] == payload["threshold_percent"]
        assert data["enabled"] == 1

    def test_create_duplicate_watchlist_item(self, client: TestClient) -> None:
        """测试重复创建返回 409."""
        payload = {
            "market_hash_name": "Duplicate Item",
            "threshold_percent": 5.0,
        }
        r1 = client.post("/api/watchlist", json=payload)
        assert r1.status_code == 200
        r2 = client.post("/api/watchlist", json=payload)
        assert r2.status_code == 409

    def test_update_watchlist_item(self, client: TestClient) -> None:
        """测试更新监控清单项."""
        payload = {
            "market_hash_name": "Update Item",
            "threshold_percent": 5.0,
        }
        client.post("/api/watchlist", json=payload)
        update = {"threshold_percent": 10.0, "enabled": False}
        response = client.put("/api/watchlist/Update%20Item", json=update)
        assert response.status_code == 200
        data = response.json()
        assert data["threshold_percent"] == 10.0
        assert data["enabled"] == 0

    def test_update_nonexistent_item(self, client: TestClient) -> None:
        """测试更新不存在的项返回 404."""
        response = client.put(
            "/api/watchlist/Nonexistent",
            json={"threshold_percent": 10.0},
        )
        assert response.status_code == 404

    def test_delete_watchlist_item(self, client: TestClient) -> None:
        """测试删除监控清单项."""
        payload = {
            "market_hash_name": "Delete Item",
            "threshold_percent": 5.0,
        }
        client.post("/api/watchlist", json=payload)
        response = client.delete("/api/watchlist/Delete%20Item")
        assert response.status_code == 200
        # 删除后应为空
        get_resp = client.get("/api/watchlist")
        assert all(
            item["market_hash_name"] != "Delete Item"
            for item in get_resp.json()
        )

    def test_delete_nonexistent_item(self, client: TestClient) -> None:
        """测试删除不存在的项返回 404."""
        response = client.delete("/api/watchlist/Nonexistent")
        assert response.status_code == 404


class TestAlertsEndpoint:
    """告警记录端点测试."""

    def test_get_alerts_empty(self, client: TestClient) -> None:
        """测试空告警记录返回空列表."""
        response = client.get("/api/alerts")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_alerts_with_data(self, client: TestClient) -> None:
        """测试查询告警记录."""
        # 先写入几条告警
        db = client.app.state.db
        db.insert_alert_log(
            market_hash_name="AK-47 | Redline",
            alert_type="rise",
            current_price=100.0,
            baseline_price=90.0,
            change_percent=11.11,
        )
        db.insert_alert_log(
            market_hash_name="AWP | Asiimov",
            alert_type="drop",
            current_price=80.0,
            baseline_price=100.0,
            change_percent=-20.0,
        )

        response = client.get("/api/alerts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {item["market_hash_name"] for item in data}
        assert "AWP | Asiimov" in names
        assert "AK-47 | Redline" in names

    def test_get_alerts_filter_by_type(self, client: TestClient) -> None:
        """测试按类型过滤告警."""
        db = client.app.state.db
        db.insert_alert_log(
            market_hash_name="Item A",
            alert_type="rise",
            current_price=100.0,
        )
        db.insert_alert_log(
            market_hash_name="Item B",
            alert_type="drop",
            current_price=80.0,
        )

        response = client.get("/api/alerts?alert_type=rise")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["alert_type"] == "rise"

    def test_get_alerts_pagination(self, client: TestClient) -> None:
        """测试告警分页."""
        db = client.app.state.db
        for i in range(5):
            db.insert_alert_log(
                market_hash_name=f"Item {i}",
                alert_type="rise",
                current_price=float(i),
            )

        response = client.get("/api/alerts?page=1&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = client.get("/api/alerts?page=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_alert_stats(self, client: TestClient) -> None:
        """测试告警统计接口."""
        db = client.app.state.db
        db.insert_alert_log(
            market_hash_name="Item A",
            alert_type="rise",
            current_price=100.0,
        )
        db.insert_alert_log(
            market_hash_name="Item B",
            alert_type="rise",
            current_price=90.0,
        )
        db.insert_alert_log(
            market_hash_name="Item C",
            alert_type="drop",
            current_price=80.0,
        )

        response = client.get("/api/alerts/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_day" in data
        assert "by_type" in data
        assert data["total"] == 3
