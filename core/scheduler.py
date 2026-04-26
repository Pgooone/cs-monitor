"""APScheduler 定时任务管理."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from api.steamdt import SteamDTClient
from config import MonitorConfig
from core.extreme_tracker import ExtremeTracker
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
        self.extreme_tracker = ExtremeTracker(client, db, config)
        self.scheduler = BackgroundScheduler()

    def _run_monitor(self) -> None:
        """执行普通监控采集."""
        self.monitor.collect_prices()

    def _run_extreme_tracker(self) -> None:
        """执行极致追踪采集."""
        self.extreme_tracker.tick()

    def start(self) -> None:
        """启动调度器并注册任务."""
        self._add_monitor_job()
        self._add_extreme_tracker_job()
        self._add_archive_job()
        self._add_item_sync_job()
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

    def _run_archive(self) -> None:
        """执行价格记录归档."""
        try:
            result = self.db.archive_old_price_records(days=90)
            logger.info(
                f"定时归档完成: 聚合 {result['aggregated']} 条, "
                f"归档 {result['archived']} 条, 删除 {result['deleted']} 条"
            )
        except Exception:
            logger.exception("价格记录归档失败")

    def _add_archive_job(self) -> None:
        """注册每日归档任务（每天凌晨 3 点执行）."""
        self.scheduler.add_job(
            self._run_archive,
            trigger=CronTrigger(hour=3, minute=0),
            id="archive_prices",
            name="价格记录归档",
            replace_existing=True,
        )
        logger.info("归档任务已注册，每天凌晨 3:00 执行")

    def _run_item_sync(self) -> None:
        """同步全量饰品基础信息（每天 1 次）."""
        try:
            if not self.db.needs_item_sync():
                logger.debug("饰品数据未过期，跳过同步")
                return
            logger.info("📦 开始定时同步全量饰品数据...")
            response = self.client.get_all_items()
            if response.get("success"):
                items_data = response.get("data") or []
                count = self.db.bulk_upsert_items(items_data)
                logger.info(f"✅ 定时饰品同步完成，共 {count} 条")
            else:
                logger.warning(
                    f"⚠️ 定时饰品同步失败: {response.get('errorMsg', '未知错误')}"
                )
        except Exception:
            logger.exception("定时饰品同步异常")

    def _add_item_sync_job(self) -> None:
        """注册每日饰品同步任务（每天凌晨 4 点执行）."""
        self.scheduler.add_job(
            self._run_item_sync,
            trigger=CronTrigger(hour=4, minute=0),
            id="item_sync",
            name="全量饰品同步",
            replace_existing=True,
        )
        logger.info("饰品同步任务已注册，每天凌晨 4:00 执行")

    def shutdown(self, wait: bool = True) -> None:
        """优雅关闭调度器."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("调度器已关闭")
