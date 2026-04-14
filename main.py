"""CS2 饰品价格波动监控系统主入口."""

from loguru import logger

from config import MonitorConfig


def main() -> None:
    """主函数."""
    logger.info("🚀 CS2 Monitor 启动中...")
    config = MonitorConfig.from_env()
    logger.info(f"当前通知渠道: {config.notify_channel}")
    logger.info("✅ 初始化完成，调度器尚未启动（等待开发完成）")


if __name__ == "__main__":
    main()
