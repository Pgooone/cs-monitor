"""APScheduler 定时任务管理."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from api.steamdt import SteamDTClient
from config import MonitorConfig
from core.monitor import PriceMonitor
from storage.database import Database


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
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        """启动调度器并注册任务."""
        self._add_monitor_job()
        self.scheduler.start()
        logger.info("调度器已启动")

        # 首次启动立即执行一次价格采集
        logger.info("首次启动，立即执行一次价格采集")
        self.monitor.collect_prices()

    def _add_monitor_job(self) -> None:
        """注册普通监控定时任务."""
        interval = max(1, self.config.check_interval_minutes)
        self.scheduler.add_job(
            self.monitor.collect_prices,
            trigger=IntervalTrigger(minutes=interval),
            id="normal_monitor",
            name="普通监控价格采集",
            replace_existing=True,
        )
        logger.info(f"普通监控任务已注册，间隔: {interval} 分钟")

    def shutdown(self, wait: bool = True) -> None:
        """优雅关闭调度器."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("调度器已关闭")
