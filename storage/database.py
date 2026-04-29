"""SQLite 数据库连接与操作封装."""

from __future__ import annotations

import sqlite3
import threading
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
        self._local = threading.local()
        self._init_tables()

    def _connect(self) -> sqlite3.Connection:
        """获取线程本地数据库连接（首次创建时执行 PRAGMA 优化）."""
        conn = getattr(self._local, "connection", None)
        if conn is not None:
            try:
                conn.execute("SELECT 1")
                return conn
            except sqlite3.ProgrammingError:
                self._local.connection = None

        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA cache_size = -64000")
        conn.execute("PRAGMA temp_store = MEMORY")
        self._local.connection = conn
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

    def _init_tables(self) -> None:
        """首次运行时自动建表."""
        with self._cursor() as cursor:
            for sql in ALL_TABLES:
                cursor.execute(sql)

        # 迁移：为旧 items 表添加 name / last_synced_at 列
        self._migrate_items_table()

        logger.info("数据库表初始化完成")

    def _migrate_items_table(self) -> None:
        """为旧版 items 表添加新列（如果不存在）."""
        with self._cursor() as cursor:
            cursor.execute("PRAGMA table_info(items)")
            columns = {row[1] for row in cursor.fetchall()}

            if "name" not in columns:
                cursor.execute("ALTER TABLE items ADD COLUMN name TEXT")
                logger.info("items 表已添加 name 列")

            if "last_synced_at" not in columns:
                cursor.execute(
                    "ALTER TABLE items ADD COLUMN last_synced_at TIMESTAMP"
                )
                logger.info("items 表已添加 last_synced_at 列")

            if "icon_url" not in columns:
                cursor.execute("ALTER TABLE items ADD COLUMN icon_url TEXT")
                logger.info("items 表已添加 icon_url 列")

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

    def bulk_upsert_items(self, items: list[dict[str, str]]) -> int:
        """批量插入或更新饰品基础信息（来自 get_all_items API）.

        Args:
            items: [{"marketHashName": "...", "name": "..."}, ...]

        Returns:
            实际写入/更新的记录数.
        """
        count = 0
        with self._cursor() as cursor:
            for item in items:
                mhn = item.get("marketHashName", "")
                name = item.get("name", "")
                icon_url = item.get("icon_url")
                if not mhn:
                    continue
                cursor.execute(
                    """
                    INSERT INTO items (market_hash_name, name, icon_url, last_synced_at)
                    VALUES (?, ?, ?, datetime('now'))
                    ON CONFLICT(market_hash_name) DO UPDATE SET
                        name = excluded.name,
                        icon_url = COALESCE(excluded.icon_url, items.icon_url),
                        last_synced_at = datetime('now')
                    """,
                    (mhn, name, icon_url),
                )
                count += 1
        logger.info(f"批量写入/更新 {count} 条饰品基础信息")
        return count

    def search_items(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """本地模糊搜索饰品（LIKE 匹配，支持中英文、无分隔符匹配）.

        搜索策略：
        1. 精确子串匹配（LIKE %query%）
        2. 若无结果，将查询拆分为 token 逐词匹配（如 "ak47" → "ak" + "47"）

        Args:
            query: 搜索关键词（支持 marketHashName 或 name）
            limit: 返回数量上限

        Returns:
            [{"market_hash_name": "...", "name": "..."}, ...]
        """
        if not query.strip():
            return []

        q = query.strip()
        like_param = f"%{q}%"

        with self._cursor() as cursor:
            # 策略 1：精确子串匹配
            cursor.execute(
                """
                SELECT market_hash_name, name, icon_url
                FROM items
                WHERE market_hash_name LIKE ? COLLATE NOCASE
                   OR name LIKE ? COLLATE NOCASE
                ORDER BY
                    CASE
                        WHEN market_hash_name LIKE ? COLLATE NOCASE THEN 0
                        WHEN name LIKE ? COLLATE NOCASE THEN 1
                        ELSE 2
                    END,
                    LENGTH(market_hash_name),
                    market_hash_name
                LIMIT ?
                """,
                (like_param, like_param, f"%{q}%", f"%{q}%", limit),
            )
            rows = cursor.fetchall()
            if rows:
                return [dict(r) for r in rows]

            # 策略 2：拆分 token 逐词匹配（如 "ak47" → ["ak", "47"]）
            import re
            tokens = re.findall(r'[a-zA-Z]+|\d+', q)
            tokens = [t for t in tokens if len(t) >= 2]
            if not tokens:
                return []

            conditions = []
            params: list[str] = []
            for token in tokens:
                conditions.append(
                    "(market_hash_name LIKE ? COLLATE NOCASE OR name LIKE ? COLLATE NOCASE)"
                )
                params.extend([f"%{token}%", f"%{token}%"])

            # 排序：以 token 开头的优先 > 非 Sticker 优先 > 短名称优先
            first_token = tokens[0]
            sql = f"""
                SELECT market_hash_name, name, icon_url
                FROM items
                WHERE {' AND '.join(conditions)}
                ORDER BY
                    CASE WHEN market_hash_name LIKE ? COLLATE NOCASE THEN 0 ELSE 1 END,
                    CASE WHEN market_hash_name LIKE 'Sticker %' THEN 1 ELSE 0 END,
                    LENGTH(market_hash_name),
                    market_hash_name
                LIMIT ?
            """
            params.extend([f"{first_token}%", str(limit)])
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def update_item_icon_url(self, market_hash_name: str, icon_url: str) -> bool:
        """更新指定饰品的图标 URL，不存在则插入."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO items (market_hash_name, icon_url, last_synced_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(market_hash_name) DO UPDATE SET
                    icon_url = excluded.icon_url,
                    last_synced_at = CURRENT_TIMESTAMP
                """,
                (market_hash_name, icon_url),
            )
            return cursor.rowcount > 0

    def get_item_icon_url(self, market_hash_name: str) -> str | None:
        """获取指定饰品的图标 URL."""
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT icon_url FROM items WHERE market_hash_name = ?",
                (market_hash_name,),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def get_items_count(self) -> int:
        """获取 items 表记录数."""
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM items")
            row = cursor.fetchone()
            return row[0] if row else 0

    def needs_item_sync(self) -> bool:
        """检查是否需要同步全量饰品数据（表为空或上次同步超过 20 小时）."""
        count = self.get_items_count()
        if count == 0:
            return True
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT last_synced_at FROM items
                WHERE last_synced_at IS NOT NULL
                ORDER BY last_synced_at DESC LIMIT 1
                """
            )
            row = cursor.fetchone()
            if not row or not row[0]:
                return True
            # 检查是否超过 20 小时
            cursor.execute(
                """
                SELECT julianday('now') - julianday(?) > 20.0/24.0
                """,
                (row[0],),
            )
            check = cursor.fetchone()
            return bool(check and check[0])

    def clean_zero_price_alerts(self) -> int:
        """清理 current_price=0 的历史脏告警数据."""
        with self._cursor() as cursor:
            cursor.execute(
                "DELETE FROM alert_logs WHERE current_price = 0"
            )
            deleted = cursor.rowcount
            if deleted > 0:
                logger.info(f"已清理 {deleted} 条 current_price=0 的脏告警数据")
            return deleted

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
            sql = """
                SELECT * FROM alert_logs
                WHERE market_hash_name = ? AND alert_type = ?
                  AND notified_at >= datetime('now', ?)
                ORDER BY notified_at DESC
            """
            cursor.execute(sql, (market_hash_name, alert_type, f"-{hours} hours"))
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
            sql = """
                SELECT * FROM extreme_track_alerts
                WHERE market_hash_name = ? AND platform = ? AND alert_type = ?
                  AND notified_at >= datetime('now', ?)
                ORDER BY notified_at DESC
            """
            cursor.execute(sql, (market_hash_name, platform, alert_type, f"-{seconds} seconds"))
            return [dict(row) for row in cursor.fetchall()]

    def get_extreme_alerts(
        self,
        page: int = 1,
        limit: int = 20,
        alert_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        market_hash_name: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """分页查询极致追踪告警记录，返回 (数据列表, 总条数)."""
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
            cursor.execute(
                f"SELECT COUNT(*) FROM extreme_track_alerts WHERE {where_clause}",
                tuple(params),
            )
            total = cursor.fetchone()[0]

            offset = (page - 1) * limit
            cursor.execute(
                f"""
                SELECT eta.*, COALESCE(i.name, i.display_name) AS display_name
                FROM extreme_track_alerts eta
                LEFT JOIN items i ON eta.market_hash_name = i.market_hash_name
                WHERE {where_clause}
                ORDER BY eta.notified_at DESC
                LIMIT ? OFFSET ?
                """,
                tuple(params) + (limit, offset),
            )
            rows = [dict(row) for row in cursor.fetchall()]
            return rows, total

    def get_extreme_alert_stats(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """返回极致追踪告警 (按天统计, 按类型统计)."""
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
            cursor.execute(
                f"""
                SELECT date(notified_at) AS date, alert_type, COUNT(*) AS count
                FROM extreme_track_alerts
                WHERE {where_clause}
                GROUP BY date(notified_at), alert_type
                ORDER BY date(notified_at) DESC
                """,
                tuple(params),
            )
            by_day = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                f"""
                SELECT 'all' AS date, alert_type, COUNT(*) AS count
                FROM extreme_track_alerts
                WHERE {where_clause}
                GROUP BY alert_type
                ORDER BY count DESC
                """,
                tuple(params),
            )
            by_type = [dict(row) for row in cursor.fetchall()]

            return by_day, by_type

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
        fields: list[str] = []
        values: list[Any] = []
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

    def get_watchlist_threshold(self, market_hash_name: str) -> float | None:
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
                    SELECT etc.*, COALESCE(i.name, i.display_name) AS display_name,
                           i.icon_url
                    FROM extreme_track_config etc
                    LEFT JOIN items i ON etc.market_hash_name = i.market_hash_name
                    WHERE etc.enabled = 1
                    ORDER BY etc.created_at
                    """
                )
            else:
                cursor.execute(
                    """
                    SELECT etc.*, COALESCE(i.name, i.display_name) AS display_name,
                           i.icon_url
                    FROM extreme_track_config etc
                    LEFT JOIN items i ON etc.market_hash_name = i.market_hash_name
                    ORDER BY etc.created_at
                    """
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

    def get_today_collection_count(self) -> int:
        """查询今日价格采集次数（按采集批次统计）."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM (
                    SELECT recorded_at
                    FROM price_records
                    WHERE recorded_at >= date('now')
                    GROUP BY strftime('%Y-%m-%d %H:%M', recorded_at)
                )
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
            conditions.append("a.market_hash_name LIKE ?")
            params.append(f"%{market_hash_name}%")

        where_clause = " AND ".join(conditions)

        with self._cursor() as cursor:
            # 总条数
            cursor.execute(
                f"SELECT COUNT(*) FROM alert_logs a WHERE {where_clause}",
                tuple(params),
            )
            total = cursor.fetchone()[0]

            # 分页数据
            offset = (page - 1) * limit
            cursor.execute(
                f"""
                SELECT a.*, w.display_name AS display_name
                FROM alert_logs a
                LEFT JOIN watchlist w ON a.market_hash_name = w.market_hash_name
                WHERE {where_clause}
                ORDER BY a.notified_at DESC
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
        """获取监控清单及其最新价格，附带24h变化和7天sparkline."""
        with self._cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    """
                    SELECT w.*,
                           pr.price AS latest_price,
                           pr.platform,
                           pr.recorded_at AS price_updated_at,
                           i.icon_url
                    FROM watchlist w
                    LEFT JOIN (
                        SELECT market_hash_name, platform, price, recorded_at
                        FROM (
                            SELECT market_hash_name, platform, price, recorded_at,
                                   ROW_NUMBER() OVER (
                                       PARTITION BY market_hash_name
                                       ORDER BY recorded_at DESC, platform
                                   ) AS rn
                            FROM price_records
                            WHERE price > 0
                        ) ranked
                        WHERE ranked.rn = 1
                    ) pr ON w.market_hash_name = pr.market_hash_name
                    LEFT JOIN items i ON w.market_hash_name = i.market_hash_name
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
                           pr.recorded_at AS price_updated_at,
                           i.icon_url
                    FROM watchlist w
                    LEFT JOIN (
                        SELECT market_hash_name, platform, price, recorded_at
                        FROM (
                            SELECT market_hash_name, platform, price, recorded_at,
                                   ROW_NUMBER() OVER (
                                       PARTITION BY market_hash_name
                                       ORDER BY recorded_at DESC, platform
                                   ) AS rn
                            FROM price_records
                            WHERE price > 0
                        ) ranked
                        WHERE ranked.rn = 1
                    ) pr ON w.market_hash_name = pr.market_hash_name
                    LEFT JOIN items i ON w.market_hash_name = i.market_hash_name
                    ORDER BY w.created_at
                    """
                )
            rows = [dict(row) for row in cursor.fetchall()]

            if not rows:
                return rows

            names = [r["market_hash_name"] for r in rows]
            placeholders = ",".join("?" * len(names))

            # 获取最近7天价格历史用于 sparkline 和 24h 变化
            cursor.execute(
                f"""
                SELECT market_hash_name, price, recorded_at
                FROM price_records
                WHERE market_hash_name IN ({placeholders})
                  AND recorded_at >= datetime('now', '-7 days')
                ORDER BY market_hash_name, recorded_at ASC
                """,
                tuple(names),
            )
            history_rows = [dict(r) for r in cursor.fetchall()]

            # 获取最接近24小时前的价格
            cursor.execute(
                f"""
                SELECT market_hash_name, price
                FROM price_records
                WHERE market_hash_name IN ({placeholders})
                  AND recorded_at >= datetime('now', '-25 hours')
                  AND recorded_at <= datetime('now', '-23 hours')
                ORDER BY market_hash_name,
                         ABS(julianday(recorded_at) - julianday(datetime('now', '-24 hours')))
                """,
                tuple(names),
            )
            price_24h_rows = cursor.fetchall()
            price_24h_by_name: dict[str, float] = {}
            for p in price_24h_rows:
                name = p["market_hash_name"]
                if name not in price_24h_by_name:
                    price_24h_by_name[name] = p["price"]

            # 按饰品分组历史价格
            history_by_name: dict[str, list[dict]] = {}
            for h in history_rows:
                name = h["market_hash_name"]
                history_by_name.setdefault(name, []).append(h)

            for row in rows:
                name = row["market_hash_name"]
                hist = history_by_name.get(name, [])

                # sparkline: 每天最后一个价格点
                daily_prices: dict[str, float] = {}
                for h in hist:
                    day = str(h["recorded_at"])[:10]
                    daily_prices[day] = h["price"]
                row["sparkline"] = list(daily_prices.values())

                # 24h 变化
                latest = row.get("latest_price")
                prev = price_24h_by_name.get(name)
                if latest is not None and prev is not None and prev > 0:
                    row["change_24h"] = round(
                        ((latest - prev) / prev) * 100, 2
                    )
                else:
                    row["change_24h"] = None

                # 各平台最新价格
                cursor.execute(
                    """
                    SELECT pr.platform, pr.price
                    FROM price_records pr
                    INNER JOIN (
                        SELECT platform, MAX(recorded_at) AS max_at
                        FROM price_records
                        WHERE market_hash_name = ?
                        GROUP BY platform
                    ) latest ON pr.platform = latest.platform
                        AND pr.recorded_at = latest.max_at
                    WHERE pr.market_hash_name = ?
                    ORDER BY pr.price ASC
                    """,
                    (name, name),
                )
                row["platform_prices"] = [
                    {"platform": r["platform"], "price": r["price"]}
                    for r in cursor.fetchall()
                ]

            return rows

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

        if days:
            conditions.append("recorded_at >= datetime('now', ?)")
            params.append(f"-{days} days")

        where_clause = " AND ".join(conditions)

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

    def get_daily_prices(
        self, market_hash_name: str, days: int = 30
    ) -> list[dict[str, Any]]:
        """按天聚合价格（取每天均价），用于趋势分析."""
        with self._cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    date(recorded_at) AS date,
                    AVG(price) AS price
                FROM price_records
                WHERE market_hash_name = ?
                  AND recorded_at >= datetime('now', '-{days} days')
                GROUP BY date(recorded_at)
                ORDER BY date(recorded_at) ASC
                """,
                (market_hash_name,),
            )
            rows = [dict(row) for row in cursor.fetchall()]
            for row in rows:
                row["price"] = round(row["price"], 2)
            return rows

    # ------------------------------------------------------------------
    # 归档操作
    # ------------------------------------------------------------------
    def archive_old_price_records(
        self, days: int = 90
    ) -> dict[str, Any]:
        """归档 90 天以上的价格记录：按天聚合后写入 archived_prices，然后删除原记录."""
        with self._cursor() as cursor:
            # 1. 查询需要归档的 90 天以上数据，按天聚合
            cursor.execute(
                f"""
                SELECT
                    market_hash_name,
                    platform,
                    date(recorded_at) AS date,
                    AVG(price) AS avg_price,
                    MIN(price) AS min_price,
                    MAX(price) AS max_price,
                    COUNT(*) AS record_count
                FROM price_records
                WHERE recorded_at < datetime('now', '-{days} days')
                GROUP BY market_hash_name, platform, date(recorded_at)
                ORDER BY date(recorded_at)
                """
            )
            rows = cursor.fetchall()
            if not rows:
                return {"archived": 0, "deleted": 0, "aggregated": 0}

            # 2. 插入归档表
            archived_count = 0
            for row in rows:
                try:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO archived_prices
                        (market_hash_name, platform, date, avg_price, min_price, max_price, record_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["market_hash_name"],
                            row["platform"],
                            row["date"],
                            round(row["avg_price"], 2),
                            row["min_price"],
                            row["max_price"],
                            row["record_count"],
                        ),
                    )
                    archived_count += 1
                except Exception:
                    continue

            # 3. 删除已归档的原始记录
            cursor.execute(
                f"""
                DELETE FROM price_records
                WHERE recorded_at < datetime('now', '-{days} days')
                """
            )
            deleted_count = cursor.rowcount

            logger.info(
                f"价格记录归档完成：聚合 {len(rows)} 条天级记录，"
                f"归档 {archived_count} 条，删除 {deleted_count} 条原始记录"
            )
            return {
                "archived": archived_count,
                "deleted": deleted_count,
                "aggregated": len(rows),
            }

    def get_all_alerts(self) -> list[dict[str, Any]]:
        """获取所有告警记录（用于基准价重算）."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT a.id, a.market_hash_name, a.current_price,
                       COALESCE(w.threshold_percent, 5.0) AS threshold_percent
                FROM alert_logs a
                LEFT JOIN watchlist w ON a.market_hash_name = w.market_hash_name
                ORDER BY a.notified_at DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_alert_baseline(
        self,
        alert_id: int,
        baseline_price: float,
        change_percent: float,
        alert_type: str | None = None,
    ) -> None:
        """更新单条告警的基准价、波动幅度和类型."""
        if alert_type:
            with self._cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE alert_logs
                    SET baseline_price = ?, change_percent = ?, alert_type = ?
                    WHERE id = ?
                    """,
                    (baseline_price, change_percent, alert_type, alert_id),
                )
        else:
            with self._cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE alert_logs
                    SET baseline_price = ?, change_percent = ?
                    WHERE id = ?
                    """,
                    (baseline_price, change_percent, alert_id),
                )

    def get_archived_price_history(
        self,
        market_hash_name: str,
        days: int | None = None,
        platform: str | None = None,
    ) -> list[dict[str, Any]]:
        """查询归档价格历史."""
        conditions = ["market_hash_name = ?"]
        params: list[Any] = [market_hash_name]
        if platform:
            conditions.append("platform = ?")
            params.append(platform)

        if days:
            conditions.append("date >= date('now', ?)")
            params.append(f"-{days} days")

        where_clause = " AND ".join(conditions)

        with self._cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM archived_prices
                WHERE {where_clause}
                ORDER BY date DESC
                """,
                tuple(params),
            )
            return [dict(row) for row in cursor.fetchall()]
