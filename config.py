"""CS2 Monitor 配置管理."""

from dataclasses import dataclass, field
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass
class MonitorConfig:
    """监控配置类."""

    # === API 配置 ===
    api_key: str = ""
    api_base_url: str = "https://open.steamdt.com"
    request_timeout: int = 30
    request_retry: int = 3

    # === 监控配置 ===
    check_interval_minutes: int = 30
    default_threshold_percent: float = 5.0
    alert_cooldown_hours: int = 4
    timezone: str = "Asia/Shanghai"

    # === 通知配置 ===
    notify_channel: str = "wecom"
    wecom_webhook_url: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_proxy: str = ""
    serverchan_sendkey: str = ""

    # === 监控清单 ===
    watchlist: list = field(default_factory=lambda: [
        {"name": "AK-47 | Redline (Field-Tested)", "threshold": 5.0},
        {"name": "AWP | Asiimov (Field-Tested)", "threshold": 5.0},
    ])

    # === Web 服务配置 ===
    web_host: str = "0.0.0.0"
    web_port: int = 8080

    # === 认证配置 ===
    admin_password: str = "admin"
    jwt_secret: str = "change-me-in-production"
    jwt_expiry_hours: int = 24

    # === 极致追踪配置 ===
    extreme_track_list: list = field(default_factory=list)

    def is_default_credentials(self) -> bool:
        """检查是否使用了默认的弱密码或 JWT secret."""
        return self.admin_password == "admin" or self.jwt_secret == "change-me-in-production"

    @classmethod
    def from_env(cls) -> "MonitorConfig":
        """从环境变量加载配置."""
        return cls(
            api_key=getenv("STEAMDT_API_KEY", ""),
            api_base_url=getenv("STEAMDT_API_BASE_URL", "https://open.steamdt.com"),
            request_timeout=int(getenv("REQUEST_TIMEOUT", "30")),
            request_retry=int(getenv("REQUEST_RETRY", "3")),
            check_interval_minutes=int(getenv("CHECK_INTERVAL_MINUTES", "30")),
            default_threshold_percent=float(getenv("DEFAULT_THRESHOLD_PERCENT", "5.0")),
            alert_cooldown_hours=int(getenv("ALERT_COOLDOWN_HOURS", "4")),
            timezone=getenv("TIMEZONE", "Asia/Shanghai"),
            web_host=getenv("WEB_HOST", "0.0.0.0"),
            web_port=int(getenv("WEB_PORT", "8080")),
            admin_password=getenv("ADMIN_PASSWORD", "admin"),
            jwt_secret=getenv("JWT_SECRET", "change-me-in-production"),
            jwt_expiry_hours=int(getenv("JWT_EXPIRY_HOURS", "24")),
            notify_channel=getenv("NOTIFY_CHANNEL", "wecom"),
            wecom_webhook_url=getenv("WECOM_WEBHOOK_URL", ""),
            telegram_bot_token=getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=getenv("TELEGRAM_CHAT_ID", ""),
            telegram_proxy=getenv("TELEGRAM_PROXY", ""),
            serverchan_sendkey=getenv("SERVERCHAN_SENDKEY", ""),
        )
