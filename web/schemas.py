"""FastAPI Pydantic 数据模型."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """健康检查响应."""

    status: str = "ok"
    version: str = "1.0.0"


class DashboardSummary(BaseModel):
    """Dashboard 概览数据."""

    active_watchlist: int = Field(0, description="监控清单数量")
    extreme_track_count: int = Field(0, description="极致追踪数量")
    today_alert_count: int = Field(0, description="今日告警数量")
    latest_price_count: int = Field(0, description="最新价格记录数")
    last_update: str | None = Field(None, description="最后更新时间")


class AlertRecord(BaseModel):
    """告警记录模型."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    market_hash_name: str
    alert_type: str
    current_price: float | None = None
    baseline_price: float | None = None
    change_percent: float | None = None
    notified_at: datetime


class PriceRecord(BaseModel):
    """价格记录模型."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    market_hash_name: str
    platform: str
    price: float
    recorded_at: datetime
