"""Web API 测试."""

import tempfile

import pytest
from fastapi.testclient import TestClient

from config import MonitorConfig
from storage.database import Database
from web.app import create_app


@pytest.fixture
def client():
    """创建 TestClient（自动携带 JWT Token）."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = Database(tmp.name)

    config = MonitorConfig(
        api_key="test_key",
        admin_password="testpass",
        jwt_secret="test-secret",
        watchlist=[{"name": "Test Item", "threshold": 5.0}],
    )

    app = create_app(db, config)
    with TestClient(app) as tc:
        # 登录获取 JWT 令牌
        resp = tc.post("/api/auth/login", json={"password": "testpass"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        tc.headers["Authorization"] = f"Bearer {token}"
        yield tc


class TestAuthEndpoint:
    """认证端点测试."""

    def test_login_success(self, client: TestClient) -> None:
        """测试正确密码登录成功."""
        response = client.post("/api/auth/login", json={"password": "testpass"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "requires_password_change" in data
        assert data["requires_password_change"] is False

    def test_login_default_password(self, client: TestClient) -> None:
        """测试默认密码登录返回 requires_password_change=True."""
        # 使用默认密码创建新客户端
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db = Database(tmp.name)
        from web.app import create_app
        config = MonitorConfig(
            admin_password="admin",
            jwt_secret="test-secret",
        )
        app = create_app(db, config)
        with TestClient(app) as c:
            response = c.post("/api/auth/login", json={"password": "admin"})
            assert response.status_code == 200
            data = response.json()
            assert data["requires_password_change"] is True

    def test_login_failure(self, client: TestClient) -> None:
        """测试错误密码登录失败."""
        response = client.post("/api/auth/login", json={"password": "wrongpass"})
        assert response.status_code == 401

    def test_me_endpoint(self, client: TestClient) -> None:
        """测试 /api/auth/me 返回用户信息."""
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_access_protected_without_token(self, client: TestClient) -> None:
        """测试未携带 Token 访问受保护接口返回 401."""
        # 临时移除 Authorization header
        original = client.headers.pop("Authorization", None)
        try:
            response = client.get("/api/watchlist")
            assert response.status_code == 401
        finally:
            if original:
                client.headers["Authorization"] = original

    def test_access_protected_with_invalid_token(self, client: TestClient) -> None:
        """测试携带无效 Token 访问受保护接口返回 401."""
        original = client.headers.get("Authorization", "")
        client.headers["Authorization"] = "Bearer invalid-token"
        try:
            response = client.get("/api/watchlist")
            assert response.status_code == 401
        finally:
            client.headers["Authorization"] = original

    def test_change_password_success(self, client: TestClient) -> None:
        """测试修改密码成功."""
        response = client.post(
            "/api/auth/change-password",
            json={"current_password": "testpass", "new_password": "newpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_change_password_wrong_current(self, client: TestClient) -> None:
        """测试修改密码时当前密码错误."""
        response = client.post(
            "/api/auth/change-password",
            json={"current_password": "wrongpass", "new_password": "newpass123"},
        )
        assert response.status_code == 401

    def test_change_password_too_short(self, client: TestClient) -> None:
        """测试修改密码时新密码太短（Pydantic 校验返回 422）."""
        response = client.post(
            "/api/auth/change-password",
            json={"current_password": "testpass", "new_password": "123"},
        )
        assert response.status_code == 422


class TestHealthEndpoint:
    """健康检查端点测试."""

    def test_health_check(self, client: TestClient) -> None:
        """测试 /api/health 返回 ok（无需认证）."""
        original = client.headers.pop("Authorization", None)
        try:
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "database" in data
            assert "scheduler" in data
        finally:
            if original:
                client.headers["Authorization"] = original


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


class TestPricesEndpoint:
    """价格数据端点测试."""

    def test_get_latest_prices_empty(self, client: TestClient) -> None:
        """测试空价格记录返回空列表."""
        response = client.get("/api/prices/latest")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_latest_prices(self, client: TestClient) -> None:
        """测试获取最新价格."""
        db = client.app.state.db
        db.insert_item("AK-47 | Redline")
        db.insert_item("AWP | Asiimov")
        db.insert_price_record("AK-47 | Redline", "buff", 100.0)
        db.insert_price_record("AK-47 | Redline", "uu", 98.0)
        db.insert_price_record("AWP | Asiimov", "buff", 200.0)

        response = client.get("/api/prices/latest")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = {item["market_hash_name"] for item in data}
        assert "AK-47 | Redline" in names
        assert "AWP | Asiimov" in names

    def test_get_price_history(self, client: TestClient) -> None:
        """测试获取历史价格."""
        db = client.app.state.db
        db.insert_item("AK-47 | Redline")
        db.insert_price_record("AK-47 | Redline", "buff", 100.0)
        db.insert_price_record("AK-47 | Redline", "buff", 105.0)
        db.insert_price_record("AK-47 | Redline", "uu", 98.0)

        response = client.get("/api/prices/AK-47%20%7C%20Redline/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_price_history_with_platform_filter(self, client: TestClient) -> None:
        """测试历史价格按平台过滤."""
        db = client.app.state.db
        db.insert_item("AK-47 | Redline")
        db.insert_price_record("AK-47 | Redline", "buff", 100.0)
        db.insert_price_record("AK-47 | Redline", "uu", 98.0)

        response = client.get(
            "/api/prices/AK-47%20%7C%20Redline/history?platform=buff"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["platform"] == "buff"

    def test_get_price_by_platforms(self, client: TestClient) -> None:
        """测试获取各平台当前价."""
        db = client.app.state.db
        db.insert_item("AK-47 | Redline")
        db.insert_price_record("AK-47 | Redline", "buff", 100.0)
        db.insert_price_record("AK-47 | Redline", "uu", 98.0)

        response = client.get(
            "/api/prices/AK-47%20%7C%20Redline/platforms"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        platforms = {item["platform"] for item in data}
        assert platforms == {"buff", "uu"}


class TestExtremeTrackEndpoint:
    """极致追踪端点测试."""

    def test_get_extreme_track_empty(self, client: TestClient) -> None:
        """测试空极致追踪配置返回空列表."""
        response = client.get("/api/extreme-track")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_extreme_track_config(self, client: TestClient) -> None:
        """测试创建极致追踪配置."""
        payload = {
            "market_hash_name": "AK-47 | Redline",
            "platform": "buff",
            "interval_seconds": 30,
            "enabled": True,
            "price_change_mode": "percent",
            "price_threshold_percent": 1.0,
        }
        response = client.post("/api/extreme-track", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["market_hash_name"] == payload["market_hash_name"]
        assert data["platform"] == payload["platform"]
        assert data["interval_seconds"] == 30
        assert data["enabled"] == 1
        assert data["price_change_mode"] == "percent"
        assert data["price_threshold_percent"] == 1.0

    def test_create_duplicate_extreme_track(self, client: TestClient) -> None:
        """测试重复创建返回 409."""
        payload = {
            "market_hash_name": "Duplicate Item",
            "platform": "buff",
        }
        r1 = client.post("/api/extreme-track", json=payload)
        assert r1.status_code == 200
        r2 = client.post("/api/extreme-track", json=payload)
        assert r2.status_code == 409

    def test_update_extreme_track_config(self, client: TestClient) -> None:
        """测试更新极致追踪配置."""
        payload = {
            "market_hash_name": "Update Item",
            "platform": "buff",
            "interval_seconds": 60,
        }
        client.post("/api/extreme-track", json=payload)
        update = {"interval_seconds": 120, "enabled": False}
        response = client.put(
            "/api/extreme-track/Update%20Item/buff", json=update
        )
        assert response.status_code == 200
        data = response.json()
        assert data["interval_seconds"] == 120
        assert data["enabled"] == 0

    def test_update_nonexistent_extreme_track(self, client: TestClient) -> None:
        """测试更新不存在的配置返回 404."""
        response = client.put(
            "/api/extreme-track/Nonexistent/buff",
            json={"interval_seconds": 120},
        )
        assert response.status_code == 404

    def test_delete_extreme_track_config(self, client: TestClient) -> None:
        """测试删除极致追踪配置."""
        payload = {
            "market_hash_name": "Delete Item",
            "platform": "buff",
        }
        client.post("/api/extreme-track", json=payload)
        response = client.delete("/api/extreme-track/Delete%20Item/buff")
        assert response.status_code == 200
        get_resp = client.get("/api/extreme-track")
        assert all(
            item["market_hash_name"] != "Delete Item"
            for item in get_resp.json()
        )

    def test_delete_nonexistent_extreme_track(self, client: TestClient) -> None:
        """测试删除不存在的配置返回 404."""
        response = client.delete("/api/extreme-track/Nonexistent/buff")
        assert response.status_code == 404

    def test_toggle_extreme_track_config(self, client: TestClient) -> None:
        """测试切换极致追踪启停状态."""
        payload = {
            "market_hash_name": "Toggle Item",
            "platform": "buff",
            "enabled": True,
        }
        client.post("/api/extreme-track", json=payload)

        # 切换为禁用
        response = client.post("/api/extreme-track/Toggle%20Item/buff/toggle")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False

        # 再次切换为启用
        response = client.post("/api/extreme-track/Toggle%20Item/buff/toggle")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True

    def test_toggle_nonexistent_extreme_track(self, client: TestClient) -> None:
        """测试切换不存在的配置返回 404."""
        response = client.post("/api/extreme-track/Nonexistent/buff/toggle")
        assert response.status_code == 404
