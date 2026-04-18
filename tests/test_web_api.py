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
        assert data["active_watchlist"] == 1
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
