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
        """创建数据库连接."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
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
