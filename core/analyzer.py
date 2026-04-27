"""价格波动分析模块."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from api.steamdt import (
    SteamDTBusinessError,
    SteamDTClient,
    SteamDTError,
    SteamDTRateLimitError,
)
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
        # 7 日均价缓存：{market_hash_name: (price, fetched_at)}，TTL 6h
        self._avg_cache: dict[str, tuple[float, datetime]] = {}
        self._avg_ttl = timedelta(hours=6)

    def _get_baseline_price(self, market_hash_name: str) -> float | None:
        """获取基准价.

        优先使用 7 天均价（6h 缓存），缺失时 fallback 到 DB 最新价.
        """
        now = datetime.utcnow()

        # 1) 缓存命中
        cached = self._avg_cache.get(market_hash_name)
        if cached and now - cached[1] < self._avg_ttl:
            return cached[0]

        # 2) 调用 API，三层异常分层
        try:
            resp = self.client.get_7day_average(market_hash_name)
        except SteamDTRateLimitError as e:
            logger.warning(
                f"[analyzer] 7d avg 限流 {market_hash_name}: {e}, 退化到 DB 基线"
            )
            return self._fallback_to_db(market_hash_name)
        except (SteamDTBusinessError, SteamDTError) as e:
            logger.warning(
                f"[analyzer] 7d avg 失败 {market_hash_name}: {e}, 退化到 DB 基线"
            )
            return self._fallback_to_db(market_hash_name)

        # 3) 解析 success=false
        if not resp.get("success"):
            logger.warning(
                f"[analyzer] 7d avg 返回 success=false {market_hash_name}, 退化到 DB 基线"
            )
            return self._fallback_to_db(market_hash_name)

        # 4) 解析均价数据
        data = resp.get("data") or {}
        prices = [
            float(p["avgPrice"])
            for p in data.get("dataList", [])
            if p.get("avgPrice")
        ]
        if not prices:
            logger.debug(
                f"{market_hash_name} 7天均价无有效数据，退化到 DB 基线"
            )
            return self._fallback_to_db(market_hash_name)

        baseline = sum(prices) / len(prices)
        self._avg_cache[market_hash_name] = (baseline, now)
        logger.debug(f"{market_hash_name} 基准价使用 7天均价: {baseline:.2f}")
        return baseline

    def _fallback_to_db(self, market_hash_name: str) -> float | None:
        """Fallback：从 DB 获取最新采集价."""
        latest = self.db.get_latest_price_any_platform(market_hash_name)
        if latest:
            price = latest["price"]
            logger.debug(
                f"{market_hash_name} 基准价使用 DB 最新采集价: {price}"
            )
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
            # 过滤掉价格为0的平台（某些平台可能返回0或未收录该饰品）
            valid_prices = [r["price"] for r in platform_records if r["price"] > 0]
            if not valid_prices:
                logger.warning(f"{market_hash_name} 所有平台价格均为0，跳过分析")
                continue
            current_price = min(valid_prices)
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
                    wl_item = self.db.get_watchlist_item(market_hash_name)
                    display_name = wl_item.get("display_name") if wl_item else None
                    alert_data = {
                        "market_hash_name": market_hash_name,
                        "display_name": display_name,
                        "alert_type": "price_surge",
                        "current_price": current_price,
                        "baseline_price": baseline_price,
                        "change_percent": change_percent,
                    }
                    sent = self.notifier.send_normal_alert(alert_data)
                    if sent:
                        self.db.insert_alert_log(
                            market_hash_name,
                            "price_surge",
                            current_price=current_price,
                            baseline_price=baseline_price,
                            change_percent=change_percent,
                        )
                        alerts.append(alert_data)
                        logger.warning(
                            f"🚨 {market_hash_name} 涨价告警: "
                            f"+{change_percent:.2f}%"
                        )
                    else:
                        logger.error(
                            f"🚨 {market_hash_name} 涨价告警通知发送失败，"
                            f"未记录冷却，下次将重试"
                        )
                else:
                    logger.info(
                        f"{market_hash_name} 涨价告警在冷却期内，跳过"
                    )

            # 跌价告警
            elif change_percent <= -threshold:
                if self._check_alert_cooldown(
                    market_hash_name, "price_drop"
                ):
                    wl_item = self.db.get_watchlist_item(market_hash_name)
                    display_name = wl_item.get("display_name") if wl_item else None
                    alert_data = {
                        "market_hash_name": market_hash_name,
                        "display_name": display_name,
                        "alert_type": "price_drop",
                        "current_price": current_price,
                        "baseline_price": baseline_price,
                        "change_percent": change_percent,
                    }
                    sent = self.notifier.send_normal_alert(alert_data)
                    if sent:
                        self.db.insert_alert_log(
                            market_hash_name,
                            "price_drop",
                            current_price=current_price,
                            baseline_price=baseline_price,
                            change_percent=change_percent,
                        )
                        alerts.append(alert_data)
                        logger.warning(
                            f"🚨 {market_hash_name} 跌价告警: "
                            f"{change_percent:.2f}%"
                        )
                    else:
                        logger.error(
                            f"🚨 {market_hash_name} 跌价告警通知发送失败，"
                            f"未记录冷却，下次将重试"
                        )
                else:
                    logger.info(
                        f"{market_hash_name} 跌价告警在冷却期内，跳过"
                    )

        return alerts
