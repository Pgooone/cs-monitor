"""趋势分析模块."""

from __future__ import annotations

from typing import Any

from loguru import logger

from storage.database import Database


class TrendAnalyzer:
    """价格趋势分析器."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def analyze(self, market_hash_name: str, days: int = 30) -> dict[str, Any] | None:
        """分析指定饰品的趋势.

        Args:
            market_hash_name: 饰品市场名称.
            days: 查询最近 N 天的数据.

        Returns:
            包含趋势标签、MA均线等信息的字典，数据不足时返回 None.
        """
        daily_prices = self.db.get_daily_prices(market_hash_name, days)
        if len(daily_prices) < 5:
            logger.info(f"{market_hash_name} 历史数据不足，无法分析趋势")
            return None

        prices = [p["price"] for p in daily_prices]

        # 计算 MA 均线
        ma5 = self._calc_ma(prices, 5)
        ma10 = self._calc_ma(prices, 10)
        ma20 = self._calc_ma(prices, 20)

        # 判断趋势标签
        trend = self._detect_trend(prices)

        return {
            "market_hash_name": market_hash_name,
            "trend": trend,
            "daily_prices": daily_prices,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20,
        }

    @staticmethod
    def _calc_ma(prices: list[float], period: int) -> list[float | None]:
        """计算移动平均线.

        前 period-1 个位置用 None 填充.
        """
        result: list[float | None] = []
        for i in range(len(prices)):
            if i < period - 1:
                result.append(None)
            else:
                avg = sum(prices[i - period + 1 : i + 1]) / period
                result.append(round(avg, 2))
        return result

    @staticmethod
    def _detect_trend(prices: list[float]) -> str:
        """检测趋势标签.

        逻辑：
        - 最近连续 3 天上涨 → 连涨 (surge)
        - 最近连续 3 天下跌 → 连跌 (drop)
        - 否则 → 震荡 (oscillate)
        """
        if len(prices) < 3:
            return "unknown"

        recent = prices[-3:]
        if recent[0] < recent[1] < recent[2]:
            return "surge"
        if recent[0] > recent[1] > recent[2]:
            return "drop"
        return "oscillate"
