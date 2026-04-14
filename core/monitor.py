"""普通监控模式：价格采集逻辑."""

from __future__ import annotations

from typing import Any

from loguru import logger

from api.steamdt import SteamDTClient
from config import MonitorConfig
from core.analyzer import PriceAnalyzer
from storage.database import Database


class PriceMonitor:
    """普通监控器：定时批量采集饰品价格."""

    def __init__(
        self,
        client: SteamDTClient,
        db: Database,
        config: MonitorConfig,
    ) -> None:
        self.client = client
        self.db = db
        self.config = config
        self.analyzer = PriceAnalyzer(client, db, config)

    def collect_prices(self) -> list[dict[str, Any]]:
        """采集 watchlist 中所有饰品的价格并存储.

        Returns:
            采集到的价格记录列表，每条记录包含 market_hash_name、platform、price.
        """
        watchlist = self.config.watchlist
        if not watchlist:
            logger.info("监控清单为空，跳过本次采集")
            return []

        names = [
            item["name"]
            for item in watchlist
            if isinstance(item, dict) and "name" in item
        ]
        if not names:
            logger.warning("监控清单格式异常，无法提取饰品名称")
            return []

        logger.info(f"开始批量采集 {len(names)} 个饰品的价格...")
        try:
            response = self.client.get_items_batch(names)
        except Exception as e:
            logger.error(f"批量查询价格失败: {e}")
            return []

        if not response.get("success"):
            logger.error(f"SteamDT API 返回失败: {response.get('errorMsg')}")
            return []

        data = response.get("data") or []
        records: list[dict[str, Any]] = []

        for item in data:
            market_hash_name = item.get("marketHashName")
            if not market_hash_name:
                continue

            # 确保 items 表中有记录（外键约束）
            self.db.insert_item(market_hash_name)

            platform_data = item.get("dataList") or []
            for platform_info in platform_data:
                platform = platform_info.get("platform")
                price = platform_info.get("sellPrice")
                if platform is None or price is None:
                    continue

                self.db.insert_price_record(
                    market_hash_name, platform, float(price)
                )
                records.append({
                    "market_hash_name": market_hash_name,
                    "platform": platform,
                    "price": float(price),
                })

        logger.info(f"本次采集完成，共写入 {len(records)} 条价格记录")

        # 采集完成后执行波动分析
        if records:
            alerts = self.analyzer.analyze(records)
            logger.info(f"本次分析触发 {len(alerts)} 条告警")

        return records
