"""APScheduler 定时任务管理."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from api.steamdt import SteamDTClient, SteamDTError, SteamDTRateLimitError
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
        self.tz = ZoneInfo(config.timezone)
        self.scheduler = BackgroundScheduler(timezone=config.timezone)
        self._last_synced_at: datetime | None = None

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

        # 重算所有告警基准价（前日 K 线收盘价）
        logger.info("正在重算告警基准价（前日收盘）...")
        recalculated = self.monitor.analyzer.recalculate_all_baselines()
        logger.info(f"告警基准价重算完成，更新 {recalculated} 条")

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
        """注册极致追踪定时任务.

        始终注册 job（即使当前列表为空），因为用户可能在运行时通过 Web 添加追踪项。
        ExtremeTracker.tick() 内部已有空列表检查，不会产生无效调用。
        """
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
            trigger=CronTrigger(hour=3, minute=0, timezone=self.tz),
            id="archive_prices",
            name="价格记录归档",
            replace_existing=True,
        )
        logger.info(f"归档任务已注册，每天凌晨 3:00 执行 ({self.config.timezone})")

    def _run_item_sync(self) -> None:
        """同步全量饰品基础信息（每天 1 次，内存级 20h 防抖）."""
        now = datetime.now()
        if self._last_synced_at and now - self._last_synced_at < timedelta(hours=20):
            logger.debug(
                f"[scheduler] item sync 20h 内已执行"
                f"(上次: {self._last_synced_at:%Y-%m-%d %H:%M})，跳过"
            )
            return

        if not self.db.needs_item_sync():
            logger.debug("饰品数据未过期，跳过同步")
            return

        logger.info("📦 开始定时同步全量饰品数据...")
        try:
            response = self.client.get_all_items()
        except SteamDTRateLimitError as e:
            logger.warning(f"[scheduler] item sync 限流: {e}")
            return
        except SteamDTError as e:
            logger.error(f"[scheduler] item sync 失败: {e}")
            return

        if response.get("success"):
            items_data = response.get("data") or []
            count = self.db.bulk_upsert_items(items_data)
            self._last_synced_at = now
            logger.info(f"✅ 定时饰品同步完成，共 {count} 条")
        else:
            logger.warning(
                f"⚠️ 定时饰品同步失败: {response.get('errorMsg', '未知错误')}"
            )

    def _add_item_sync_job(self) -> None:
        """注册每日饰品同步任务（每天凌晨 4 点执行）."""
        self.scheduler.add_job(
            self._run_item_sync,
            trigger=CronTrigger(hour=4, minute=0, timezone=self.tz),
            id="item_sync",
            name="全量饰品同步",
            replace_existing=True,
        )
        logger.info(f"饰品同步任务已注册，每天凌晨 4:00 执行 ({self.config.timezone})")

    def shutdown(self, wait: bool = True) -> None:
        """优雅关闭调度器."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("调度器已关闭")
