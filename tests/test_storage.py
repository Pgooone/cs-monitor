"""存储模块单元测试."""

import tempfile
from pathlib import Path

import pytest

from storage.database import Database


class TestDatabase:
    """测试 Database 类."""

    @pytest.fixture
    def db(self):
        """创建临时数据库."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield Database(db_path)

    def test_init_tables(self, db):
        """测试自动建表."""
        # 初始化时不应报错，且表应已存在
        with db._cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row["name"] for row in cursor.fetchall()}
            assert "items" in tables
            assert "price_records" in tables
            assert "alert_logs" in tables
            assert "extreme_track_snapshots" in tables
            assert "extreme_track_alerts" in tables

    def test_insert_and_get_item(self, db):
        """测试饰品插入和查询."""
        db.insert_item("AK-47 | Redline (Field-Tested)", "AK-47 红线", "rifle")
        item = db.get_item("AK-47 | Redline (Field-Tested)")
        assert item is not None
        assert item["market_hash_name"] == "AK-47 | Redline (Field-Tested)"
        assert item["display_name"] == "AK-47 红线"

    def test_insert_price_record_and_get_latest(self, db):
        """测试价格记录写入和读取."""
        db.insert_item("AK-47 | Redline (Field-Tested)")
        db.insert_price_record("AK-47 | Redline (Field-Tested)", "BUFF", 125.0)
        latest = db.get_latest_price("AK-47 | Redline (Field-Tested)", "BUFF")
        assert latest is not None
        assert latest["price"] == 125.0
        assert latest["platform"] == "BUFF"

    def test_insert_alert_log_and_get_recent(self, db):
        """测试告警记录写入和查询."""
        db.insert_alert_log(
            "AK-47 | Redline (Field-Tested)",
            "price_surge",
            current_price=130.0,
            baseline_price=120.0,
            change_percent=8.33,
        )
        alerts = db.get_recent_alerts(
            "AK-47 | Redline (Field-Tested)", "price_surge", hours=4
        )
        assert len(alerts) == 1
        assert alerts[0]["current_price"] == 130.0

    def test_insert_extreme_snapshot_and_get_latest(self, db):
        """测试极致追踪快照写入和读取."""
        db.insert_extreme_snapshot(
            "AK-47 | Redline (Field-Tested)", "youpin", 128.5, 42
        )
        latest = db.get_latest_snapshot(
            "AK-47 | Redline (Field-Tested)", "youpin"
        )
        assert latest is not None
        assert latest["price"] == 128.5
        assert latest["quantity"] == 42

    def test_insert_extreme_alert_and_get_latest(self, db):
        """测试极致追踪告警写入和读取."""
        db.insert_extreme_alert(
            "AK-47 | Redline (Field-Tested)",
            "youpin",
            "price_change",
            prev_price=125.0,
            curr_price=128.5,
            price_change_percent=2.8,
        )
        latest = db.get_latest_extreme_alert(
            "AK-47 | Redline (Field-Tested)", "youpin", "price_change"
        )
        assert latest is not None
        assert latest["prev_price"] == 125.0
        assert latest["curr_price"] == 128.5

    def test_archive_old_price_records_empty(self, db):
        """测试空数据归档不报错."""
        result = db.archive_old_price_records(days=90)
        assert result["archived"] == 0
        assert result["deleted"] == 0
        assert result["aggregated"] == 0

    def test_archive_old_price_records(self, db):
        """测试归档 90 天以上价格记录."""
        import sqlite3

        db.insert_item("AK-47 | Redline")
        db.insert_item("AWP | Asiimov")

        # 插入近期记录（不应被归档）
        db.insert_price_record("AK-47 | Redline", "buff", 100.0)
        db.insert_price_record("AK-47 | Redline", "buff", 102.0)

        # 直接插入 91 天前的记录（模拟旧数据）
        with db._cursor() as cursor:
            old_date = "date('now', '-91 days')"
            cursor.execute(
                f"""
                INSERT INTO price_records (market_hash_name, platform, price, recorded_at)
                VALUES ('AK-47 | Redline', 'buff', 90.0, {old_date})
                """
            )
            cursor.execute(
                f"""
                INSERT INTO price_records (market_hash_name, platform, price, recorded_at)
                VALUES ('AK-47 | Redline', 'buff', 92.0, {old_date})
                """
            )
            cursor.execute(
                f"""
                INSERT INTO price_records (market_hash_name, platform, price, recorded_at)
                VALUES ('AWP | Asiimov', 'uu', 200.0, {old_date})
                """
            )

        result = db.archive_old_price_records(days=90)
        assert result["aggregated"] == 2  # 2 个饰品各 1 条天级记录
        assert result["archived"] == 2
        assert result["deleted"] == 3

        # 验证归档表数据
        archived = db.get_archived_price_history("AK-47 | Redline")
        assert len(archived) == 1
        assert archived[0]["avg_price"] == 91.0
        assert archived[0]["record_count"] == 2

        # 验证近期记录仍在 price_records 中
        recent = db.get_price_history("AK-47 | Redline")
        assert len(recent) == 2
