"""SteamDT API 客户端封装."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any

import httpx
from loguru import logger


@dataclass
class SteamDTConfig:
    """SteamDT 客户端配置."""

    api_key: str
    base_url: str = "https://open.steamdt.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 10


class SteamDTClient:
    """SteamDT 开放平台 API 客户端."""

    def __init__(self, config: SteamDTConfig) -> None:
        self.config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """发送 HTTP 请求，带重试和随机延迟."""
        # 请求前随机延迟 1-3 秒，避免触发风控
        delay = random.uniform(1.0, 3.0)
        logger.debug(f"SteamDT 请求延迟 {delay:.2f}s: {method} {path}")
        time.sleep(delay)

        last_exception: Exception | None = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = self._client.request(method, path, **kwargs)
                response.raise_for_status()
                data = response.json()
                logger.debug(f"SteamDT 响应: {method} {path} -> success={data.get('success')}")
                return data
            except httpx.HTTPStatusError as e:
                logger.warning(f"SteamDT HTTP 错误 (尝试 {attempt}/{self.config.max_retries}): {e.response.status_code} - {e.response.text}")
                last_exception = e
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay)
            except httpx.RequestError as e:
                logger.warning(f"SteamDT 请求错误 (尝试 {attempt}/{self.config.max_retries}): {e}")
                last_exception = e
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay)

        raise SteamDTAPIError(f"SteamDT 请求失败（已重试 {self.config.max_retries} 次）: {last_exception}") from last_exception

    def get_items_batch(self, market_hash_names: list[str]) -> dict[str, Any]:
        """通过 marketHashName 批量查询饰品价格.

        Args:
            market_hash_names: 饰品名称列表，1-100 个.

        Returns:
            API 原始响应字典.
        """
        if not market_hash_names:
            return {"success": True, "data": []}
        if len(market_hash_names) > 100:
            raise ValueError("market_hash_names 最多支持 100 个")

        return self._request(
            "POST",
            "/open/cs2/v1/price/batch",
            json={"marketHashNames": market_hash_names},
        )

    def get_7day_average(self, market_hash_name: str) -> dict[str, Any]:
        """通过 MarketHashName 查询所有平台近 7 天均价.

        Args:
            market_hash_name: 饰品名称.

        Returns:
            API 原始响应字典.
        """
        return self._request(
            "GET",
            "/open/cs2/v1/price/avg",
            params={"marketHashName": market_hash_name},
        )

    def get_all_items(self) -> dict[str, Any]:
        """获取 Steam 饰品基础信息（每天只能调用 1 次）.

        Returns:
            API 原始响应字典.
        """
        return self._request("GET", "/open/cs2/v1/base")

    def get_item_kline(
        self,
        market_hash_name: str,
        kline_type: int,
        platform: str = "ALL",
        special_style: str | None = None,
    ) -> dict[str, Any]:
        """查询 Steam 饰品 K 线数据.

        Args:
            market_hash_name: 饰品名称.
            kline_type: 1=时K, 2=日K, 3=周K.
            platform: 平台，默认 ALL.
            special_style: 特殊款式.

        Returns:
            API 原始响应字典.
        """
        payload: dict[str, Any] = {
            "marketHashName": market_hash_name,
            "type": kline_type,
            "platform": platform,
        }
        if special_style is not None:
            payload["specialStyle"] = special_style
        return self._request("POST", "/open/cs2/item/v1/kline", json=payload)

    def close(self) -> None:
        """关闭 HTTP 客户端."""
        self._client.close()

    def __enter__(self) -> SteamDTClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class SteamDTAPIError(Exception):
    """SteamDT API 调用异常."""
