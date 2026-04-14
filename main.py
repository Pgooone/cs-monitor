"""CS2 饰品价格波动监控系统主入口."""

import signal
import sys

from loguru import logger

from api.steamdt import SteamDTClient, SteamDTConfig
from config import MonitorConfig
from core.scheduler import MonitorScheduler
from storage.database import Database


def main() -> None:
    """主函数."""
    logger.info("🚀 CS2 Monitor 启动中...")

    # 加载配置
    config = MonitorConfig.from_env()
    if not config.api_key:
        logger.error("❌ 未配置 STEAMDT_API_KEY，请在 .env 中设置后重试")
        sys.exit(1)

    logger.info(f"✅ 配置加载完成，通知渠道: {config.notify_channel}")

    # 初始化数据库
    db = Database("data/prices.db")
    logger.info("✅ 数据库初始化完成")

    # 初始化 SteamDT 客户端
    steamdt_config = SteamDTConfig(
        api_key=config.api_key,
        base_url=config.api_base_url,
        timeout=config.request_timeout,
        max_retries=config.request_retry,
    )
    client = SteamDTClient(steamdt_config)
    logger.info("✅ SteamDT 客户端初始化完成")

    # 初始化调度器
    scheduler = MonitorScheduler(client, db, config)

    # 注册 Ctrl+C 信号处理
    def signal_handler(signum, frame):
        logger.info("🛑 收到中断信号，正在优雅退出...")
        scheduler.shutdown(wait=True)
        client.close()
        logger.info("👋 已安全退出")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动调度器
    scheduler.start()
    logger.info("✅ 调度器已启动，系统运行中...")

    # 主循环：保持程序运行
    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
