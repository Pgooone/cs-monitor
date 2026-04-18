"""SQLite 数据库连接与操作封装."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from loguru import logger

from storage.models import ALL_TABLES


class Database:
    """SQLite 数据库管理类."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _connect(self) -> sqlite3.Connection:
        """创建数据库连接（启用 WAL 模式）."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    @contextmanager
    def _cursor(self):
        """上下文管理器：自动提交/回滚."""
        conn = self._connect()
        try:
            yield conn.cursor()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_tables(self) -> None:
        """首次运行时自动建表."""
        with self._cursor() as cursor:
            for sql in ALL_TABLES:
                cursor.execute(sql)
        logger.info("数据库表初始化完成")

    # ------------------------------------------------------------------
    # items 表操作
    # ------------------------------------------------------------------
    def insert_item(
        self,
        market_hash_name: str,
        display_name: str | None = None,
        category: str | None = None,
    ) -> None:
        """插入或忽略饰品基础信息."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT OR IGNORE INTO items (market_hash_name, display_name, category)
                VALUES (?, ?, ?)
                """,
                (market_hash_name, display_name, category),
            )

    def get_item(self, market_hash_name: str) -> dict[str, Any] | None:
        """查询单条饰品信息."""
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT * FROM items WHERE market_hash_name = ?",
                (market_hash_name,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # ------------------------------------------------------------------
    # price_records 表操作
    # ------------------------------------------------------------------
    def insert_price_record(
        self,
        market_hash_name: str,
        platform: str,
        price: float,
    ) -> None:
        """写入价格记录."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO price_records (market_hash_name, platform, price)
                VALUES (?, ?, ?)
                """,
                (market_hash_name, platform, price),
            )

    def get_latest_price(
        self,
        market_hash_name: str,
        platform: str,
    ) -> dict[str, Any] | None:
        """获取指定饰品和平台的最新价格记录."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM price_records
                WHERE market_hash_name = ? AND platform = ?
                ORDER BY recorded_at DESC
                LIMIT 1
                """,
                (market_hash_name, platform),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_latest_price_any_platform(
        self,
        market_hash_name: str,
    ) -> dict[str, Any] | None:
        """获取指定饰品的最新价格记录（不区分平台）."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM price_records
                WHERE market_hash_name = ?
                ORDER BY recorded_at DESC
                LIMIT 1
                """,
                (market_hash_name,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # ------------------------------------------------------------------
    # alert_logs 表操作
    # ------------------------------------------------------------------
    def insert_alert_log(
        self,
        market_hash_name: str,
        alert_type: str,
        current_price: float | None = None,
        baseline_price: float | None = None,
        change_percent: float | None = None,
    ) -> None:
        """写入普通监控告警记录."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO alert_logs
                (market_hash_name, alert_type, current_price, baseline_price, change_percent)
                VALUES (?, ?, ?, ?, ?)
                """,
                (market_hash_name, alert_type, current_price, baseline_price, change_percent),
            )

    def get_recent_alerts(
        self,
        market_hash_name: str,
        alert_type: str,
        hours: int = 4,
    ) -> list[dict[str, Any]]:
        """查询最近 N 小时内的同类告警记录."""
        with self._cursor() as cursor:
            # SQLite 不支持在字符串字面量中用参数绑定，使用字符串拼接
            sql = f"""
                SELECT * FROM alert_logs
                WHERE market_hash_name = ? AND alert_type = ?
                  AND notified_at >= datetime('now', '-{hours} hours')
                ORDER BY notified_at DESC
            """
            cursor.execute(sql, (market_hash_name, alert_type))
            return [dict(row) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # extreme_track_snapshots 表操作
    # ------------------------------------------------------------------
    def insert_extreme_snapshot(
        self,
        market_hash_name: str,
        platform: str,
        price: float | None = None,
        quantity: int | None = None,
    ) -> None:
        """写入极致追踪快照."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO extreme_track_snapshots
                (market_hash_name, platform, price, quantity)
                VALUES (?, ?, ?, ?)
                """,
                (market_hash_name, platform, price, quantity),
            )

    def get_latest_snapshot(
        self,
        market_hash_name: str,
        platform: str,
    ) -> dict[str, Any] | None:
        """获取指定饰品和平台的最新快照."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM extreme_track_snapshots
                WHERE market_hash_name = ? AND platform = ?
                ORDER BY recorded_at DESC
                LIMIT 1
                """,
                (market_hash_name, platform),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # ------------------------------------------------------------------
    # extreme_track_alerts 表操作
    # ------------------------------------------------------------------
    def insert_extreme_alert(
        self,
        market_hash_name: str,
        platform: str,
        alert_type: str,
        prev_price: float | None = None,
        curr_price: float | None = None,
        price_change_percent: float | None = None,
        prev_quantity: int | None = None,
        curr_quantity: int | None = None,
        quantity_change_percent: float | None = None,
    ) -> None:
        """写入极致追踪告警记录."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO extreme_track_alerts
                (market_hash_name, platform, alert_type,
                 prev_price, curr_price, price_change_percent,
                 prev_quantity, curr_quantity, quantity_change_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    market_hash_name,
                    platform,
                    alert_type,
                    prev_price,
                    curr_price,
                    price_change_percent,
                    prev_quantity,
                    curr_quantity,
                    quantity_change_percent,
                ),
            )

    def get_latest_extreme_alert(
        self,
        market_hash_name: str,
        platform: str,
        alert_type: str,
    ) -> dict[str, Any] | None:
        """获取指定饰品、平台、类型的最新极致追踪告警."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM extreme_track_alerts
                WHERE market_hash_name = ? AND platform = ? AND alert_type = ?
                ORDER BY notified_at DESC
                LIMIT 1
                """,
                (market_hash_name, platform, alert_type),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_recent_extreme_alerts(
        self,
        market_hash_name: str,
        platform: str,
        alert_type: str,
        seconds: int = 0,
    ) -> list[dict[str, Any]]:
        """查询最近 N 秒内的同类极致追踪告警记录."""
        with self._cursor() as cursor:
            sql = f"""
                SELECT * FROM extreme_track_alerts
                WHERE market_hash_name = ? AND platform = ? AND alert_type = ?
                  AND notified_at >= datetime('now', '-{seconds} seconds')
                ORDER BY notified_at DESC
            """
            cursor.execute(sql, (market_hash_name, platform, alert_type))
            return [dict(row) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # watchlist 表操作
    # ------------------------------------------------------------------
    def insert_watchlist_item(
        self,
        market_hash_name: str,
        display_name: str | None = None,
        threshold_percent: float = 5.0,
        enabled: bool = True,
    ) -> None:
        """插入监控清单项."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO watchlist
                (market_hash_name, display_name, threshold_percent, enabled, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (market_hash_name, display_name, threshold_percent, 1 if enabled else 0),
            )

    def get_watchlist(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        """获取监控清单."""
        with self._cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    """
                    SELECT * FROM watchlist
                    WHERE enabled = 1
                    ORDER BY created_at
                    """
                )
            else:
                cursor.execute("SELECT * FROM watchlist ORDER BY created_at")
            return [dict(row) for row in cursor.fetchall()]

    def get_watchlist_item(
        self, market_hash_name: str
    ) -> dict[str, Any] | None:
        """获取单个监控项."""
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT * FROM watchlist WHERE market_hash_name = ?",
                (market_hash_name,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_watchlist_item(
        self,
        market_hash_name: str,
        display_name: str | None = None,
        threshold_percent: float | None = None,
        enabled: bool | None = None,
    ) -> None:
        """更新监控清单项."""
        fields = []
        values = []
        if display_name is not None:
            fields.append("display_name = ?")
            values.append(display_name)
        if threshold_percent is not None:
            fields.append("threshold_percent = ?")
            values.append(threshold_percent)
        if enabled is not None:
            fields.append("enabled = ?")
            values.append(1 if enabled else 0)
        if not fields:
            return
        fields.append("updated_at = datetime('now')")
        values.append(market_hash_name)
        with self._cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE watchlist
                SET {', '.join(fields)}
                WHERE market_hash_name = ?
                """,
                tuple(values),
            )

    def delete_watchlist_item(self, market_hash_name: str) -> None:
        """删除监控清单项."""
        with self._cursor() as cursor:
            cursor.execute(
                "DELETE FROM watchlist WHERE market_hash_name = ?",
                (market_hash_name,),
            )

    def get_watchlist_threshold(self, market_hash_name: str) -> float:
        """获取指定饰品的阈值，不存在则返回 None."""
        item = self.get_watchlist_item(market_hash_name)
        if item:
            return float(item["threshold_percent"])
        return None

    # ------------------------------------------------------------------
    # extreme_track_config 表操作
    # ------------------------------------------------------------------
    def insert_extreme_track_config(
        self,
        market_hash_name: str,
        platform: str,
        interval_seconds: int = 60,
        enabled: bool = True,
        price_track_enabled: bool = True,
        price_change_mode: str = "any",
        price_threshold_percent: float = 0.0,
        quantity_track_enabled: bool = True,
        quantity_change_mode: str = "any",
        quantity_threshold_percent: float = 0.0,
        alert_cooldown_seconds: int = 0,
        quiet_hours_start: str | None = None,
        quiet_hours_end: str | None = None,
    ) -> None:
        """插入或更新极致追踪配置."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO extreme_track_config
                (market_hash_name, platform, interval_seconds, enabled,
                 price_track_enabled, price_change_mode, price_threshold_percent,
                 quantity_track_enabled, quantity_change_mode, quantity_threshold_percent,
                 alert_cooldown_seconds, quiet_hours_start, quiet_hours_end, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    market_hash_name, platform, interval_seconds, 1 if enabled else 0,
                    1 if price_track_enabled else 0, price_change_mode, price_threshold_percent,
                    1 if quantity_track_enabled else 0, quantity_change_mode, quantity_threshold_percent,
                    alert_cooldown_seconds, quiet_hours_start, quiet_hours_end,
                ),
            )

    def get_extreme_track_configs(
        self, enabled_only: bool = True
    ) -> list[dict[str, Any]]:
        """获取极致追踪配置列表."""
        with self._cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    """
                    SELECT * FROM extreme_track_config
                    WHERE enabled = 1
                    ORDER BY created_at
                    """
                )
            else:
                cursor.execute(
                    "SELECT * FROM extreme_track_config ORDER BY created_at"
                )
            return [dict(row) for row in cursor.fetchall()]

    def get_extreme_track_config(
        self, market_hash_name: str, platform: str
    ) -> dict[str, Any] | None:
        """获取单个极致追踪配置."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM extreme_track_config
                WHERE market_hash_name = ? AND platform = ?
                """,
                (market_hash_name, platform),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_extreme_track_config(
        self,
        market_hash_name: str,
        platform: str,
        **kwargs: Any,
    ) -> None:
        """更新极致追踪配置."""
        allowed = {
            "interval_seconds", "enabled", "price_track_enabled",
            "price_change_mode", "price_threshold_percent",
            "quantity_track_enabled", "quantity_change_mode",
            "quantity_threshold_percent", "alert_cooldown_seconds",
            "quiet_hours_start", "quiet_hours_end",
        }
        fields = []
        values = []
        for key, value in kwargs.items():
            if key not in allowed:
                continue
            if isinstance(value, bool):
                value = 1 if value else 0
            fields.append(f"{key} = ?")
            values.append(value)
        if not fields:
            return
        fields.append("updated_at = datetime('now')")
        values.extend([market_hash_name, platform])
        with self._cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE extreme_track_config
                SET {', '.join(fields)}
                WHERE market_hash_name = ? AND platform = ?
                """,
                tuple(values),
            )

    def delete_extreme_track_config(
        self, market_hash_name: str, platform: str
    ) -> None:
        """删除极致追踪配置."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM extreme_track_config
                WHERE market_hash_name = ? AND platform = ?
                """,
                (market_hash_name, platform),
            )

    # ------------------------------------------------------------------
    # system_config 表操作
    # ------------------------------------------------------------------
    def set_system_config(self, key: str, value: str) -> None:
        """设置系统配置项."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO system_config (key, value, updated_at)
                VALUES (?, ?, datetime('now'))
                """,
                (key, value),
            )

    def get_system_config(self, key: str) -> str | None:
        """获取系统配置项."""
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT value FROM system_config WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    # ------------------------------------------------------------------
    # 默认数据导入
    # ------------------------------------------------------------------
    def import_default_watchlist(self, watchlist: list[dict]) -> None:
        """首次启动时从 config.py 默认值导入监控清单."""
        existing = self.get_watchlist(enabled_only=False)
        if existing:
            logger.info("watchlist 表已有数据，跳过默认导入")
            return
        for item in watchlist:
            if isinstance(item, dict) and "name" in item:
                self.insert_watchlist_item(
                    market_hash_name=item["name"],
                    display_name=item.get("display_name"),
                    threshold_percent=item.get("threshold", 5.0),
                    enabled=item.get("enabled", True),
                )
                logger.info(f"已导入默认监控项: {item['name']}")

    def import_default_extreme_track(self, track_list: list[dict]) -> None:
        """首次启动时从 config.py 默认值导入极致追踪配置."""
        existing = self.get_extreme_track_configs(enabled_only=False)
        if existing:
            logger.info("extreme_track_config 表已有数据，跳过默认导入")
            return
        for item in track_list:
            if not isinstance(item, dict):
                continue
            self.insert_extreme_track_config(
                market_hash_name=item.get("market_hash_name", ""),
                platform=item.get("platform", ""),
                interval_seconds=item.get("interval_seconds", 60),
                enabled=item.get("enabled", True),
                price_track_enabled=item.get("price_track_enabled", True),
                price_change_mode=item.get("price_change_mode", "any"),
                price_threshold_percent=item.get("price_threshold_percent", 0.0),
                quantity_track_enabled=item.get("quantity_track_enabled", True),
                quantity_change_mode=item.get("quantity_change_mode", "any"),
                quantity_threshold_percent=item.get("quantity_threshold_percent", 0.0),
                alert_cooldown_seconds=item.get("alert_cooldown_seconds", 0),
                quiet_hours_start=item.get("quiet_hours_start"),
                quiet_hours_end=item.get("quiet_hours_end"),
            )
            logger.info(
                f"已导入默认极致追踪: {item.get('market_hash_name')}@{item.get('platform')}"
            )

    # ------------------------------------------------------------------
    # 统计查询（Dashboard 用）
    # ------------------------------------------------------------------
    def get_today_alert_count(self) -> int:
        """查询今日告警数量."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM alert_logs
                WHERE notified_at >= date('now')
                """
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    def get_latest_price_records_count(self) -> int:
        """查询最新价格记录数（每饰品每平台各取最新）."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM (
                    SELECT market_hash_name, platform
                    FROM price_records
                    GROUP BY market_hash_name, platform
                )
                """
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    def get_latest_price_record_any(self) -> dict[str, Any] | None:
        """获取任意最新一条价格记录."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM price_records
                ORDER BY recorded_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # ------------------------------------------------------------------
    # alerts 查询（分页、过滤、统计）
    # ------------------------------------------------------------------
    def get_alerts(
        self,
        page: int = 1,
        limit: int = 20,
        alert_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        market_hash_name: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """分页查询告警记录，返回 (数据列表, 总条数)."""
        conditions = ["1 = 1"]
        params: list[Any] = []
        if alert_type:
            conditions.append("alert_type = ?")
            params.append(alert_type)
        if start_date:
            conditions.append("notified_at >= ?")
            params.append(f"{start_date} 00:00:00")
        if end_date:
            conditions.append("notified_at <= ?")
            params.append(f"{end_date} 23:59:59")
        if market_hash_name:
            conditions.append("market_hash_name LIKE ?")
            params.append(f"%{market_hash_name}%")

        where_clause = " AND ".join(conditions)

        with self._cursor() as cursor:
            # 总条数
            cursor.execute(
                f"SELECT COUNT(*) FROM alert_logs WHERE {where_clause}",
                tuple(params),
            )
            total = cursor.fetchone()[0]

            # 分页数据
            offset = (page - 1) * limit
            cursor.execute(
                f"""
                SELECT * FROM alert_logs
                WHERE {where_clause}
                ORDER BY notified_at DESC
                LIMIT ? OFFSET ?
                """,
                tuple(params) + (limit, offset),
            )
            rows = [dict(row) for row in cursor.fetchall()]
            return rows, total

    def get_alert_stats(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """返回 (按天统计, 按类型统计)."""
        conditions = ["1 = 1"]
        params: list[Any] = []
        if start_date:
            conditions.append("notified_at >= ?")
            params.append(f"{start_date} 00:00:00")
        if end_date:
            conditions.append("notified_at <= ?")
            params.append(f"{end_date} 23:59:59")

        where_clause = " AND ".join(conditions)

        with self._cursor() as cursor:
            # 按天统计
            cursor.execute(
                f"""
                SELECT date(notified_at) AS date, alert_type, COUNT(*) AS count
                FROM alert_logs
                WHERE {where_clause}
                GROUP BY date(notified_at), alert_type
                ORDER BY date(notified_at) DESC
                """,
                tuple(params),
            )
            by_day = [dict(row) for row in cursor.fetchall()]

            # 按类型统计
            cursor.execute(
                f"""
                SELECT 'all' AS date, alert_type, COUNT(*) AS count
                FROM alert_logs
                WHERE {where_clause}
                GROUP BY alert_type
                ORDER BY count DESC
                """,
                tuple(params),
            )
            by_type = [dict(row) for row in cursor.fetchall()]

            return by_day, by_type

    # ------------------------------------------------------------------
    # watchlist 扩展查询
    # ------------------------------------------------------------------
    def get_watchlist_count(self, enabled_only: bool = True) -> int:
        """获取监控清单数量."""
        with self._cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    "SELECT COUNT(*) FROM watchlist WHERE enabled = 1"
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM watchlist")
            row = cursor.fetchone()
            return row[0] if row else 0

    def get_watchlist_with_latest_price(
        self, enabled_only: bool = True
    ) -> list[dict[str, Any]]:
        """获取监控清单及其最新价格."""
        with self._cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    """
                    SELECT w.*,
                           pr.price AS latest_price,
                           pr.platform,
                           pr.recorded_at AS price_updated_at
                    FROM watchlist w
                    LEFT JOIN (
                        SELECT market_hash_name, platform, price, recorded_at
                        FROM price_records p1
                        WHERE recorded_at = (
                            SELECT MAX(recorded_at)
                            FROM price_records p2
                            WHERE p2.market_hash_name = p1.market_hash_name
                        )
                    ) pr ON w.market_hash_name = pr.market_hash_name
                    WHERE w.enabled = 1
                    ORDER BY w.created_at
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT w.*,
                           pr.price AS latest_price,
                           pr.platform,
                           pr.recorded_at AS price_updated_at
                    FROM watchlist w
                    LEFT JOIN (
                        SELECT market_hash_name, platform, price, recorded_at
                        FROM price_records p1
                        WHERE recorded_at = (
                            SELECT MAX(recorded_at)
                            FROM price_records p2
                            WHERE p2.market_hash_name = p1.market_hash_name
                        )
                    ) pr ON w.market_hash_name = pr.market_hash_name
                    ORDER BY w.created_at
                    """
                )
            return [dict(row) for row in cursor.fetchall()]

    def get_extreme_track_count(self, enabled_only: bool = True) -> int:
        """获取极致追踪配置数量."""
        with self._cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    "SELECT COUNT(*) FROM extreme_track_config WHERE enabled = 1"
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM extreme_track_config"
                )
            row = cursor.fetchone()
            return row[0] if row else 0

    # ------------------------------------------------------------------
    # prices 查询（价格数据 API 用）
    # ------------------------------------------------------------------
    def get_latest_prices(self) -> list[dict[str, Any]]:
        """获取所有监控项的最新价格（每饰品每平台各取最新）."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT pr.market_hash_name, pr.platform, pr.price, pr.recorded_at
                FROM price_records pr
                INNER JOIN (
                    SELECT market_hash_name, platform, MAX(recorded_at) AS max_at
                    FROM price_records
                    GROUP BY market_hash_name, platform
                ) latest ON pr.market_hash_name = latest.market_hash_name
                    AND pr.platform = latest.platform
                    AND pr.recorded_at = latest.max_at
                ORDER BY pr.market_hash_name, pr.platform
                """
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_price_history(
        self,
        market_hash_name: str,
        days: int | None = None,
        platform: str | None = None,
    ) -> list[dict[str, Any]]:
        """获取指定饰品的历史价格记录."""
        conditions = ["market_hash_name = ?"]
        params: list[Any] = [market_hash_name]
        if platform:
            conditions.append("platform = ?")
            params.append(platform)

        where_clause = " AND ".join(conditions)
        # SQLite datetime 表达式不支持参数绑定间隔值，需字符串拼接
        if days:
            where_clause += f" AND recorded_at >= datetime('now', '-{days} days')"

        with self._cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM price_records
                WHERE {where_clause}
                ORDER BY recorded_at DESC
                """,
                tuple(params),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_price_by_platforms(
        self, market_hash_name: str
    ) -> list[dict[str, Any]]:
        """获取指定饰品在各平台的最新价格."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT pr.market_hash_name, pr.platform, pr.price, pr.recorded_at
                FROM price_records pr
                INNER JOIN (
                    SELECT platform, MAX(recorded_at) AS max_at
                    FROM price_records
                    WHERE market_hash_name = ?
                    GROUP BY platform
                ) latest ON pr.platform = latest.platform
                    AND pr.recorded_at = latest.max_at
                WHERE pr.market_hash_name = ?
                ORDER BY pr.platform
                """,
                (market_hash_name, market_hash_name),
            )
            return [dict(row) for row in cursor.fetchall()]
