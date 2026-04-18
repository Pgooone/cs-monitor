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


class WatchlistItem(BaseModel):
    """监控清单项模型."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    market_hash_name: str
    display_name: str | None = None
    threshold_percent: float = 5.0
    enabled: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WatchlistItemCreate(BaseModel):
    """创建监控清单项请求."""

    market_hash_name: str = Field(..., min_length=1, description="饰品市场名称")
    display_name: str | None = Field(None, description="显示名称")
    threshold_percent: float = Field(5.0, ge=0.1, description="告警阈值百分比")
    enabled: bool = Field(True, description="是否启用")


class WatchlistItemUpdate(BaseModel):
    """更新监控清单项请求."""

    display_name: str | None = Field(None, description="显示名称")
    threshold_percent: float | None = Field(None, ge=0.1, description="告警阈值百分比")
    enabled: bool | None = Field(None, description="是否启用")


class WatchlistItemWithPrice(BaseModel):
    """带最新价格的监控清单项."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    market_hash_name: str
    display_name: str | None = None
    threshold_percent: float = 5.0
    enabled: int = 1
    latest_price: float | None = Field(None, description="最新价格")
    platform: str | None = Field(None, description="价格来源平台")
    price_updated_at: datetime | None = Field(None, description="价格更新时间")
    created_at: datetime | None = None
    updated_at: datetime | None = None


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


class AlertRecordFilter(BaseModel):
    """告警记录查询过滤参数."""

    page: int = Field(1, ge=1, description="页码")
    limit: int = Field(20, ge=1, le=100, description="每页数量")
    alert_type: str | None = Field(None, description="告警类型过滤")
    start_date: str | None = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: str | None = Field(None, description="结束日期 (YYYY-MM-DD)")
    market_hash_name: str | None = Field(None, description="饰品名称过滤")


class AlertStatsItem(BaseModel):
    """告警统计单项."""

    date: str
    alert_type: str
    count: int


class AlertStatsResponse(BaseModel):
    """告警统计响应."""

    total: int
    by_day: list[AlertStatsItem]
    by_type: list[AlertStatsItem]


class PriceRecord(BaseModel):
    """价格记录模型."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    market_hash_name: str
    platform: str
    price: float
    recorded_at: datetime


class LatestPriceItem(BaseModel):
    """最新价格项."""

    market_hash_name: str
    platform: str
    price: float
    recorded_at: datetime


class PriceHistoryItem(BaseModel):
    """历史价格项."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    market_hash_name: str
    platform: str
    price: float
    recorded_at: datetime


class PlatformPriceItem(BaseModel):
    """各平台当前价格项."""

    market_hash_name: str
    platform: str
    price: float
    recorded_at: datetime


class ExtremeTrackConfig(BaseModel):
    """极致追踪配置模型."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    market_hash_name: str
    platform: str
    interval_seconds: int = 60
    enabled: int = 1
    price_track_enabled: int = 1
    price_change_mode: str = "any"
    price_threshold_percent: float = 0.0
    quantity_track_enabled: int = 1
    quantity_change_mode: str = "any"
    quantity_threshold_percent: float = 0.0
    alert_cooldown_seconds: int = 0
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ExtremeTrackConfigCreate(BaseModel):
    """创建极致追踪配置请求."""

    market_hash_name: str = Field(..., min_length=1, description="饰品市场名称")
    platform: str = Field(..., min_length=1, description="平台名称")
    interval_seconds: int = Field(60, ge=5, description="轮询间隔秒数")
    enabled: bool = Field(True, description="是否启用")
    price_track_enabled: bool = Field(True, description="是否追踪价格")
    price_change_mode: str = Field("any", description="价格变动模式: any/percent")
    price_threshold_percent: float = Field(0.0, ge=0.0, description="价格变动阈值")
    quantity_track_enabled: bool = Field(True, description="是否追踪数量")
    quantity_change_mode: str = Field("any", description="数量变动模式: any/percent")
    quantity_threshold_percent: float = Field(0.0, ge=0.0, description="数量变动阈值")
    alert_cooldown_seconds: int = Field(0, ge=0, description="告警冷却秒数")
    quiet_hours_start: str | None = Field(None, description="免打扰开始时间 (HH:MM)")
    quiet_hours_end: str | None = Field(None, description="免打扰结束时间 (HH:MM)")


class ExtremeTrackConfigUpdate(BaseModel):
    """更新极致追踪配置请求."""

    interval_seconds: int | None = Field(None, ge=5, description="轮询间隔秒数")
    enabled: bool | None = Field(None, description="是否启用")
    price_track_enabled: bool | None = Field(None, description="是否追踪价格")
    price_change_mode: str | None = Field(None, description="价格变动模式: any/percent")
    price_threshold_percent: float | None = Field(None, ge=0.0, description="价格变动阈值")
    quantity_track_enabled: bool | None = Field(None, description="是否追踪数量")
    quantity_change_mode: str | None = Field(None, description="数量变动模式: any/percent")
    quantity_threshold_percent: float | None = Field(None, ge=0.0, description="数量变动阈值")
    alert_cooldown_seconds: int | None = Field(None, ge=0, description="告警冷却秒数")
    quiet_hours_start: str | None = Field(None, description="免打扰开始时间 (HH:MM)")
    quiet_hours_end: str | None = Field(None, description="免打扰结束时间 (HH:MM)")


class NotifySettings(BaseModel):
    """通知配置模型."""

    notify_channel: str = Field("wecom", description="默认通知渠道")
    wecom_webhook_url: str = Field("", description="企业微信 Webhook URL")
    telegram_bot_token: str = Field("", description="Telegram Bot Token")
    telegram_chat_id: str = Field("", description="Telegram Chat ID")
    serverchan_sendkey: str = Field("", description="Server 酱 SendKey")


class NotifyTestRequest(BaseModel):
    """测试通知请求."""

    channel: str | None = Field(None, description="指定测试渠道")
    extra: dict | None = Field(None, description="额外参数（如 webhook_url）")
