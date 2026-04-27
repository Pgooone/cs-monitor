"""极致追踪模块."""

from __future__ import annotations

import time
from datetime import datetime
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


class ExtremeTracker:
    """极致追踪器：高频单品狙击."""

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
        self._next_run_at: dict[str, float] = {}

    def _track_id(self, track_config: dict) -> str:
        """生成追踪项唯一标识."""
        return f"{track_config['market_hash_name']}@{track_config['platform']}"

    def _get_interval(self, track_config: dict) -> int:
        """获取轮询间隔."""
        return track_config.get("interval_seconds", 60)

    def _is_quiet_hours(self, track_config: dict) -> bool:
        """检查当前是否处于免打扰时段."""
        start = track_config.get("quiet_hours_start", "")
        end = track_config.get("quiet_hours_end", "")
        if not start or not end:
            return False
        try:
            now = datetime.now().time()
            start_t = datetime.strptime(start, "%H:%M").time()
            end_t = datetime.strptime(end, "%H:%M").time()
            if start_t <= end_t:
                return start_t <= now <= end_t
            else:
                return now >= start_t or now <= end_t
        except ValueError:
            logger.warning(f"免打扰时间格式错误: {start}-{end}")
            return False

    def _check_cooldown(
        self,
        market_hash_name: str,
        platform: str,
        alert_type: str,
        cooldown_seconds: int,
    ) -> bool:
        """检查告警是否已过冷却期.

        Returns:
            True 表示可以告警（不在冷却期或无需冷却）.
        """
        if cooldown_seconds <= 0:
            return True
        recent = self.db.get_recent_extreme_alerts(
            market_hash_name, platform, alert_type, cooldown_seconds
        )
        return len(recent) == 0

    def _fetch_current(
        self,
        track_config: dict,
    ) -> dict[str, Any] | None:
        """获取当前价格和数量（使用 /price/single，60 次/分钟）."""
        market_hash_name = track_config["market_hash_name"]
        platform = track_config["platform"]
        try:
            response = self.client.get_item_price_single(market_hash_name)
        except SteamDTRateLimitError as e:
            logger.warning(
                f"极致追踪限流 {market_hash_name}, "
                f"retry_after={e.retry_after:.0f}s"
            )
            time.sleep(min(e.retry_after, 120))
            return None
        except SteamDTBusinessError as e:
            logger.error(
                f"极致追踪业务错误 {market_hash_name}: {e}"
            )
            return None
        except SteamDTError as e:
            logger.warning(
                f"极致追踪调用失败 {market_hash_name}: {e}"
            )
            return None

        data = response.get("data") or []
        for p in data:
            if p.get("platform") == platform:
                return {
                    "price": p.get("sellPrice"),
                    "quantity": p.get("sellCount"),
                }
        logger.warning(
            f"未找到 {market_hash_name} 在平台 {platform} 的数据"
        )
        return None

    def _detect_changes(
        self,
        track_config: dict,
        current: dict[str, Any],
        last: dict[str, Any],
    ) -> dict[str, Any] | None:
        """检测价格和数量变动."""
        price_alert = None
        qty_alert = None

        # 价格变动检测
        if track_config.get("price_track_enabled", True):
            curr_price = current.get("price")
            last_price = last.get("price")
            if (
                curr_price is not None
                and last_price is not None
                and float(last_price) != 0
            ):
                change = float(curr_price) - float(last_price)
                change_percent = (change / float(last_price)) * 100.0
                mode = track_config.get("price_change_mode", "any")
                threshold = track_config.get("price_threshold_percent", 0.0)
                if mode == "any" and change != 0:
                    price_alert = {
                        "type": "price_change",
                        "change": change,
                        "change_percent": change_percent,
                    }
                elif (
                    mode == "percent"
                    and abs(change_percent) >= threshold
                ):
                    price_alert = {
                        "type": "price_change",
                        "change": change,
                        "change_percent": change_percent,
                    }

        # 数量变动检测
        if track_config.get("quantity_track_enabled", True):
            curr_qty = current.get("quantity")
            last_qty = last.get("quantity")
            if curr_qty is not None and last_qty is not None:
                change = int(curr_qty) - int(last_qty)
                if int(last_qty) > 0:
                    change_percent = (change / int(last_qty)) * 100.0
                else:
                    change_percent = 100.0 if change > 0 else 0.0
                mode = track_config.get("quantity_change_mode", "any")
                threshold = track_config.get(
                    "quantity_threshold_percent", 0.0
                )
                if mode == "any" and change != 0:
                    qty_alert = {
                        "type": "quantity_change",
                        "change": change,
                        "change_percent": change_percent,
                    }
                elif (
                    mode == "percent"
                    and abs(change_percent) >= threshold
                ):
                    qty_alert = {
                        "type": "quantity_change",
                        "change": change,
                        "change_percent": change_percent,
                    }

        if price_alert and qty_alert:
            return {
                "alert_type": "both",
                "price_change": price_alert["change"],
                "price_change_percent": price_alert["change_percent"],
                "quantity_change": qty_alert["change"],
                "quantity_change_percent": qty_alert["change_percent"],
            }
        elif price_alert:
            return {
                "alert_type": "price_change",
                "price_change": price_alert["change"],
                "price_change_percent": price_alert["change_percent"],
            }
        elif qty_alert:
            return {
                "alert_type": "quantity_change",
                "quantity_change": qty_alert["change"],
                "quantity_change_percent": qty_alert["change_percent"],
            }
        return None

    def _track_one(
        self,
        track_config: dict,
    ) -> dict[str, Any] | None:
        """处理单个追踪项."""
        tid = self._track_id(track_config)
        market_hash_name = track_config["market_hash_name"]
        platform = track_config["platform"]

        # 免打扰检查
        if self._is_quiet_hours(track_config):
            logger.debug(f"极致追踪 [{tid}] 处于免打扰时段，跳过")
            return None

        # 获取当前数据
        current = self._fetch_current(track_config)
        if current is None:
            return None

        price = current.get("price")
        quantity = current.get("quantity")

        # 获取上一次快照
        last = self.db.get_latest_snapshot(market_hash_name, platform)

        # 写入快照
        self.db.insert_extreme_snapshot(
            market_hash_name, platform, price, quantity
        )

        # 首次采集不告警
        if last is None:
            logger.info(
                f"极致追踪 [{tid}] 首次采集，记录快照不告警"
            )
            return None

        # 检测变动
        changes = self._detect_changes(track_config, current, last)
        if changes is None:
            return None

        # 冷却检查
        alert_type = changes["alert_type"]
        cooldown = track_config.get("alert_cooldown_seconds", 0)
        if not self._check_cooldown(
            market_hash_name, platform, alert_type, cooldown
        ):
            logger.info(
                f"极致追踪 [{tid}] {alert_type} 在冷却期内，跳过"
            )
            return None

        prev_price = last.get("price")
        curr_price = current.get("price")
        prev_qty = last.get("quantity")
        curr_qty = current.get("quantity")

        price_change = changes.get("price_change", 0)
        price_change_pct = changes.get("price_change_percent", 0)
        qty_change = changes.get("quantity_change", 0)
        qty_change_pct = changes.get("quantity_change_percent", 0)

        result = {
            "track_id": tid,
            "alert_type": alert_type,
            "prev_price": prev_price,
            "curr_price": curr_price,
            "price_change": price_change,
            "price_change_percent": price_change_pct,
            "prev_quantity": prev_qty,
            "curr_quantity": curr_qty,
            "quantity_change": qty_change,
            "quantity_change_percent": qty_change_pct,
        }
        sent = self.notifier.send_extreme_alert(result, market_hash_name, platform)
        if sent:
            self.db.insert_extreme_alert(
                market_hash_name=market_hash_name,
                platform=platform,
                alert_type=alert_type,
                prev_price=prev_price,
                curr_price=curr_price,
                price_change_percent=price_change_pct,
                prev_quantity=prev_qty,
                curr_quantity=curr_qty,
                quantity_change_percent=qty_change_pct,
            )
            logger.warning(
                f"极致追踪 [{tid}] 触发 {alert_type} 告警: "
                f"价格 {prev_price}→{curr_price}, 数量 {prev_qty}→{curr_qty}"
            )
            return result
        else:
            logger.error(
                f"极致追踪 [{tid}] {alert_type} 告警通知发送失败，"
                f"未记录冷却，下次将重试"
            )
            return None

    def tick(self) -> list[dict[str, Any]]:
        """执行一轮极致追踪检查."""
        tracks = self.db.get_extreme_track_configs(enabled_only=True)
        if not tracks:
            return []

        now = time.time()
        results: list[dict[str, Any]] = []

        for track_config in tracks:
            if not track_config.get("enabled", True):
                continue

            tid = self._track_id(track_config)
            next_run = self._next_run_at.get(tid, 0)
            if now < next_run:
                continue

            result = self._track_one(track_config)
            if result:
                results.append(result)

            interval = self._get_interval(track_config)
            self._next_run_at[tid] = now + interval

        return results
