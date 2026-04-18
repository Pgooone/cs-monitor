"""价格波动分析模块."""

from __future__ import annotations

from typing import Any

from loguru import logger

from api.steamdt import SteamDTClient
from config import MonitorConfig
from notify.manager import NotificationManager
from storage.database import Database


class PriceAnalyzer:
    """价格波动分析器."""

    def __init__(
        self,
        client: SteamDTClient,
        db: Database,
        config: MonitorConfig,
    ) -> None:
        self.client = client
        self.db = db
        self.config = config
        self.notifier = NotificationManager(config)

    def _get_baseline_price(self, market_hash_name: str) -> float | None:
        """获取基准价.

        优先使用 7 天均价，缺失时使用上一次采集价格.
        """
        try:
            response = self.client.get_7day_average(market_hash_name)
            if response.get("success"):
                data = response.get("data") or {}
                avg_price = data.get("avgPrice")
                if avg_price is not None:
                    logger.debug(
                        f"{market_hash_name} 基准价使用 7天均价: {avg_price}"
                    )
                    return float(avg_price)
        except Exception as e:
            logger.warning(f"查询 {market_hash_name} 7天均价失败: {e}")

        latest = self.db.get_latest_price_any_platform(market_hash_name)
        if latest:
            price = latest["price"]
            logger.debug(f"{market_hash_name} 基准价使用上次采集价格: {price}")
            return float(price)

        return None

    def _get_threshold(self, market_hash_name: str) -> float:
        """获取指定饰品的波动阈值."""
        threshold = self.db.get_watchlist_threshold(market_hash_name)
        if threshold is not None:
            return float(threshold)
        return float(self.config.default_threshold_percent)

    def _check_alert_cooldown(
        self,
        market_hash_name: str,
        alert_type: str,
    ) -> bool:
        """检查告警是否处于冷却期.

        Returns:
            True 表示可以告警（不在冷却期），False 表示在冷却期.
        """
        recent_alerts = self.db.get_recent_alerts(
            market_hash_name,
            alert_type,
            hours=self.config.alert_cooldown_hours,
        )
        return len(recent_alerts) == 0

    def analyze(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """分析价格波动并触发告警.

        Args:
            records: 本次采集的价格记录列表.

        Returns:
            触发的告警列表.
        """
        if not records:
            return []

        # 按饰品聚合价格，取最低价为当前价
        item_prices: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            name = record["market_hash_name"]
            item_prices.setdefault(name, []).append(record)

        alerts: list[dict[str, Any]] = []

        for market_hash_name, platform_records in item_prices.items():
            current_price = min(r["price"] for r in platform_records)
            baseline_price = self._get_baseline_price(market_hash_name)

            if baseline_price is None or baseline_price == 0:
                logger.warning(
                    f"{market_hash_name} 无法获取基准价，跳过分析"
                )
                continue

            change_percent = (
                (current_price - baseline_price) / baseline_price
            ) * 100.0
            threshold = self._get_threshold(market_hash_name)

            logger.info(
                f"{market_hash_name} 当前价: {current_price:.2f}, "
                f"基准价: {baseline_price:.2f}, "
                f"波动: {change_percent:+.2f}%, 阈值: ±{threshold:.2f}%"
            )

            # 涨价告警
            if change_percent >= threshold:
                if self._check_alert_cooldown(
                    market_hash_name, "price_surge"
                ):
                    self.db.insert_alert_log(
                        market_hash_name,
                        "price_surge",
                        current_price=current_price,
                        baseline_price=baseline_price,
                        change_percent=change_percent,
                    )
                    alerts.append({
                        "market_hash_name": market_hash_name,
                        "alert_type": "price_surge",
                        "current_price": current_price,
                        "baseline_price": baseline_price,
                        "change_percent": change_percent,
                    })
                    logger.warning(
                        f"🚨 {market_hash_name} 涨价告警: "
                        f"+{change_percent:.2f}%"
                    )
                    self.notifier.send_normal_alert(alerts[-1])
                else:
                    logger.info(
                        f"{market_hash_name} 涨价告警在冷却期内，跳过"
                    )

            # 跌价告警
            elif change_percent <= -threshold:
                if self._check_alert_cooldown(
                    market_hash_name, "price_drop"
                ):
                    self.db.insert_alert_log(
                        market_hash_name,
                        "price_drop",
                        current_price=current_price,
                        baseline_price=baseline_price,
                        change_percent=change_percent,
                    )
                    alerts.append({
                        "market_hash_name": market_hash_name,
                        "alert_type": "price_drop",
                        "current_price": current_price,
                        "baseline_price": baseline_price,
                        "change_percent": change_percent,
                    })
                    logger.warning(
                        f"🚨 {market_hash_name} 跌价告警: "
                        f"{change_percent:.2f}%"
                    )
                    self.notifier.send_normal_alert(alerts[-1])
                else:
                    logger.info(
                        f"{market_hash_name} 跌价告警在冷却期内，跳过"
                    )

        return alerts
