"""趋势分析模块单元测试."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from core.trend_analyzer import TrendAnalyzer
from storage.database import Database


class TestTrendAnalyzer:
    """TrendAnalyzer 测试用例."""

    @pytest.fixture
    def db(self):
        """创建临时数据库."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            database = Database(str(db_path))
            yield database

    @pytest.fixture
    def analyzer(self, db):
        """创建 TrendAnalyzer 实例."""
        return TrendAnalyzer(db)

    def _insert_prices(self, db: Database, name: str, prices: list[float], dates: list[str]) -> None:
        """批量插入价格记录."""
        conn = sqlite3.connect(str(db.db_path))
        cursor = conn.cursor()
        for price, date in zip(prices, dates):
            cursor.execute(
                """
                INSERT INTO price_records (market_hash_name, platform, price, recorded_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, "buff", price, date),
            )
        conn.commit()
        conn.close()

    def test_analyze_surge(self, analyzer, db):
        """测试连涨趋势检测."""
        name = "AK-47 | Test (Field-Tested)"
        prices = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]
        dates = [f"2026-04-{10+i} 12:00:00" for i in range(len(prices))]
        self._insert_prices(db, name, prices, dates)

        result = analyzer.analyze(name, days=30)
        assert result is not None
        assert result["trend"] == "surge"
        assert result["market_hash_name"] == name
        assert len(result["daily_prices"]) == 6
        assert result["ma5"][-1] is not None
        assert result["ma10"][0] is None  # 前4个为None

    def test_analyze_drop(self, analyzer, db):
        """测试连跌趋势检测."""
        name = "AWP | Test (Field-Tested)"
        prices = [105.0, 104.0, 103.0, 102.0, 101.0, 100.0]
        dates = [f"2026-04-{10+i} 12:00:00" for i in range(len(prices))]
        self._insert_prices(db, name, prices, dates)

        result = analyzer.analyze(name, days=30)
        assert result is not None
        assert result["trend"] == "drop"

    def test_analyze_oscillate(self, analyzer, db):
        """测试震荡趋势检测."""
        name = "M4A4 | Test (Field-Tested)"
        prices = [100.0, 102.0, 101.0, 103.0, 102.0, 104.0]
        dates = [f"2026-04-{10+i} 12:00:00" for i in range(len(prices))]
        self._insert_prices(db, name, prices, dates)

        result = analyzer.analyze(name, days=30)
        assert result is not None
        assert result["trend"] == "oscillate"

    def test_analyze_insufficient_data(self, analyzer, db):
        """测试数据不足时返回 None."""
        name = "Glock | Test (Field-Tested)"
        prices = [100.0, 101.0, 102.0]
        dates = [f"2026-04-{10+i} 12:00:00" for i in range(len(prices))]
        self._insert_prices(db, name, prices, dates)

        result = analyzer.analyze(name, days=30)
        assert result is None

    def test_analyze_no_data(self, analyzer):
        """测试无数据时返回 None."""
        result = analyzer.analyze("Nonexistent Item", days=30)
        assert result is None

    def test_calc_ma(self):
        """测试 MA 计算."""
        prices = [10.0, 20.0, 30.0, 40.0, 50.0]
        ma3 = TrendAnalyzer._calc_ma(prices, 3)
        assert ma3[0] is None
        assert ma3[1] is None
        assert ma3[2] == 20.0
        assert ma3[3] == 30.0
        assert ma3[4] == 40.0

    def test_detect_trend_surge(self):
        """测试连涨检测."""
        assert TrendAnalyzer._detect_trend([100, 101, 102]) == "surge"
        assert TrendAnalyzer._detect_trend([98, 99, 100, 101, 102]) == "surge"

    def test_detect_trend_drop(self):
        """测试连跌检测."""
        assert TrendAnalyzer._detect_trend([102, 101, 100]) == "drop"
        assert TrendAnalyzer._detect_trend([105, 104, 103, 102, 101]) == "drop"

    def test_detect_trend_oscillate(self):
        """测试震荡检测."""
        assert TrendAnalyzer._detect_trend([100, 102, 101]) == "oscillate"
        assert TrendAnalyzer._detect_trend([100, 100, 100]) == "oscillate"
        assert TrendAnalyzer._detect_trend([100, 99, 101]) == "oscillate"

    def test_detect_trend_unknown(self):
        """测试数据不足时返回 unknown."""
        assert TrendAnalyzer._detect_trend([100]) == "unknown"
        assert TrendAnalyzer._detect_trend([100, 101]) == "unknown"
