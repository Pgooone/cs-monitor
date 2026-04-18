"""APScheduler 定时任务管理."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from api.steamdt import SteamDTClient
from config import MonitorConfig
from core.extreme_tracker import ExtremeTracker
from core.monitor import PriceMonitor
from storage.database import Database
from web.ws_manager import ws_manager


class MonitorScheduler:
    """调度器管理类."""

    def __init__(
        self,
        client: SteamDTClient,
        db: Database,
        config: MonitorConfig,
    ) -> None:
        self.client = client
        self.db = db
        self.config = config
        self.monitor = PriceMonitor(client, db, config)
        self.extreme_tracker = ExtremeTracker(client, db, config)
        self.scheduler = BackgroundScheduler()

    def _run_monitor(self) -> None:
        """执行普通监控并广播 WebSocket 告警."""
        result = self.monitor.collect_prices()
        alerts = result.get("alerts", [])
        for alert in alerts:
            ws_manager.broadcast_alert_sync({
                "type": "alert",
                "data": {
                    "market_hash_name": alert["market_hash_name"],
                    "alert_type": alert["alert_type"],
                    "current_price": alert.get("current_price"),
                    "baseline_price": alert.get("baseline_price"),
                    "change_percent": alert.get("change_percent"),
                    "timestamp": alert.get("notified_at", ""),
                },
            })

    def _run_extreme_tracker(self) -> None:
        """执行极致追踪并广播 WebSocket 消息."""
        results = self.extreme_tracker.tick()
        for result in results:
            track_id = result.get("track_id", "")
            ws_manager.broadcast_extreme_track_sync(track_id, {
                "type": "extreme_track",
                "data": {
                    "track_id": track_id,
                    "alert_type": result.get("alert_type"),
                    "prev_price": result.get("prev_price"),
                    "curr_price": result.get("curr_price"),
                    "price_change": result.get("price_change"),
                    "price_change_percent": result.get("price_change_percent"),
                    "prev_quantity": result.get("prev_quantity"),
                    "curr_quantity": result.get("curr_quantity"),
                    "quantity_change": result.get("quantity_change"),
                    "quantity_change_percent": result.get("quantity_change_percent"),
                    "timestamp": result.get("timestamp", ""),
                },
            })

    def start(self) -> None:
        """启动调度器并注册任务."""
        self._add_monitor_job()
        self._add_extreme_tracker_job()
        self.scheduler.start()
        logger.info("调度器已启动")

        # 首次启动立即执行一次价格采集
        logger.info("首次启动，立即执行一次价格采集")
        self._run_monitor()

    def _add_monitor_job(self) -> None:
        """注册普通监控定时任务."""
        interval = max(1, self.config.check_interval_minutes)
        self.scheduler.add_job(
            self._run_monitor,
            trigger=IntervalTrigger(minutes=interval),
            id="normal_monitor",
            name="普通监控价格采集",
            replace_existing=True,
        )
        logger.info(f"普通监控任务已注册，间隔: {interval} 分钟")

    def _add_extreme_tracker_job(self) -> None:
        """注册极致追踪定时任务."""
        tracks = self.db.get_extreme_track_configs(enabled_only=True)
        if not tracks:
            logger.info("极致追踪列表为空，跳过注册")
            return

        # 统一使用 10 秒 tick，由 ExtremeTracker 内部管理各追踪项的执行时间
        self.scheduler.add_job(
            self._run_extreme_tracker,
            trigger=IntervalTrigger(seconds=10),
            id="extreme_tracker",
            name="极致追踪轮询",
            replace_existing=True,
        )
        logger.info("极致追踪任务已注册，tick 间隔: 10 秒")

    def shutdown(self, wait: bool = True) -> None:
        """优雅关闭调度器."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("调度器已关闭")
