"""CS2 饰品价格波动监控系统主入口."""

from __future__ import annotations

import signal
import sys
import threading

import uvicorn
from loguru import logger

from api.steamdt import SteamDTClient, SteamDTConfig
from config import MonitorConfig
from core.scheduler import MonitorScheduler
from storage.database import Database
from web.app import create_app


def main() -> None:
    """主函数：同时启动 APScheduler + FastAPI."""
    logger.info("🚀 CS2 Monitor 启动中...")

    # 加载配置
    config = MonitorConfig.from_env()
    if not config.api_key:
        logger.error("❌ 未配置 STEAMDT_API_KEY，请在 .env 中设置后重试")
        sys.exit(1)

    # 安全检查：默认密码警告
    if config.is_default_credentials():
        logger.warning("🚨 【安全警告】正在使用默认密码或 JWT secret！")
        logger.warning("🚨 请立即修改 ADMIN_PASSWORD 和 JWT_SECRET 环境变量")
        logger.warning("🚨 在生产环境中使用默认值会导致严重的安全隐患")

    logger.info(f"✅ 配置加载完成，通知渠道: {config.notify_channel}")

    # 初始化数据库
    db = Database("data/prices.db")
    logger.info("✅ 数据库初始化完成")

    # 首次启动时从 config.py 默认值导入数据
    db.import_default_watchlist(config.watchlist)
    db.import_default_extreme_track(config.extreme_track_list)

    # B-37: 清理 current_price=0 的历史脏告警
    cleaned = db.clean_zero_price_alerts()
    if cleaned > 0:
        logger.info(f"🧹 已清理 {cleaned} 条脏告警数据")

    # 初始化 SteamDT 客户端
    steamdt_config = SteamDTConfig(
        api_key=config.api_key,
        base_url=config.api_base_url,
        timeout=config.request_timeout,
        max_retries=config.request_retry,
    )
    client = SteamDTClient(steamdt_config)
    logger.info("✅ SteamDT 客户端初始化完成")

    # B-42: 启动时同步全量饰品数据（每天限 1 次）
    if db.needs_item_sync():
        logger.info("📦 items 表为空或数据过期，开始同步全量饰品数据...")
        try:
            response = client.get_all_items()
            if response.get("success"):
                items_data = response.get("data") or []
                count = db.bulk_upsert_items(items_data)
                logger.info(f"✅ 全量饰品同步完成，共 {count} 条")
            else:
                logger.warning(
                    f"⚠️ 全量饰品同步失败: {response.get('errorMsg', '未知错误')}"
                )
        except Exception:
            logger.exception("全量饰品同步异常")
    else:
        logger.info(f"📦 items 表已有 {db.get_items_count()} 条记录，跳过同步")

    # 初始化调度器
    scheduler = MonitorScheduler(client, db, config)

    # 创建 FastAPI 应用
    app = create_app(db, config)

    # 在后台线程启动调度器
    def run_scheduler() -> None:
        try:
            scheduler.start()
            logger.info("✅ 调度器已启动，系统运行中...")
        except Exception:
            logger.exception("调度器启动失败")

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # 配置 uvicorn
    web_host = config.web_host
    web_port = config.web_port
    uvicorn_config = uvicorn.Config(
        app,
        host=web_host,
        port=web_port,
        log_level="info",
    )
    server = uvicorn.Server(uvicorn_config)

    # 注册信号处理：优雅退出
    def signal_handler(signum: int | None, frame: object | None) -> None:
        logger.info("🛑 收到中断信号，正在优雅退出...")
        scheduler.shutdown(wait=True)
        client.close()
        server.should_exit = True
        logger.info("👋 已安全退出")
        sys.exit(0)

    # uvicorn 会覆盖信号处理，所以我们在启动前设置
    # 同时使用 atexit 确保退出时清理
    original_sigint = signal.signal(signal.SIGINT, signal_handler)
    original_sigterm = signal.signal(signal.SIGTERM, signal_handler)

    logger.info(f"🌐 Web 服务启动中: http://{web_host}:{web_port}")

    try:
        server.run()
    except KeyboardInterrupt:
        signal_handler(None, None)
    finally:
        # 恢复原始信号处理
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGTERM, original_sigterm)


if __name__ == "__main__":
    main()
