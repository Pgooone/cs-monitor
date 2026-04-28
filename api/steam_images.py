"""Steam 社区市场图片获取模块.

通过 market_hash_name 从 Steam 社区市场搜索 API 获取饰品图标 URL，
并拼接为完整的 CDN 图片地址。
"""

from __future__ import annotations

import os

import httpx
from loguru import logger

STEAM_CDN_BASE = "https://community.akamai.steamstatic.com/economy/image/"
STEAM_SEARCH_URL = "https://steamcommunity.com/market/search/render/"


def _get_proxy() -> str | None:
    """从环境变量获取代理地址."""
    proxy = os.environ.get("TELEGRAM_PROXY") or os.environ.get("HTTP_PROXY")
    logger.warning(f"代理配置: TELEGRAM_PROXY={os.environ.get('TELEGRAM_PROXY')}, HTTP_PROXY={os.environ.get('HTTP_PROXY')}, 使用: {proxy}")
    return proxy


async def fetch_icon_url(market_hash_name: str) -> str | None:
    """通过 Steam 社区市场搜索 API 获取饰品图标 URL.

    优先精确匹配 market_hash_name，无精确匹配则取第一条结果。
    返回完整 CDN 图片 URL，失败返回 None。
    """
    proxy = _get_proxy()
    try:
        async with httpx.AsyncClient(timeout=15, proxy=proxy, follow_redirects=True) as client:
            resp = await client.get(
                STEAM_SEARCH_URL,
                params={
                    "query": market_hash_name,
                    "appid": 730,
                    "norender": 1,
                    "count": 1,
                    "sort_column": "popular",
                    "sort_dir": "desc",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            if not results:
                logger.debug(f"Steam 搜索无结果: {market_hash_name}")
                return None

            # 精确匹配 market_hash_name
            for item in results:
                asset = item.get("asset_description", {})
                icon = asset.get("icon_url", "")
                if icon:
                    name = item.get("hash_name", "")
                    if name == market_hash_name:
                        return f"{STEAM_CDN_BASE}{icon}"

            # 无精确匹配，取第一条结果
            first = results[0]
            icon = first.get("asset_description", {}).get("icon_url", "")
            if icon:
                return f"{STEAM_CDN_BASE}{icon}"

            return None
    except Exception as e:
        logger.warning(f"获取饰品图片失败 [{market_hash_name}]: {type(e).__name__}: {repr(e)}")
        return None


async def fetch_icon_urls_batch(
    market_hash_names: list[str],
) -> dict[str, str | None]:
    """批量获取饰品图标 URL.

    逐个请求（Steam 社区市场无批量 API），返回
    {market_hash_name: icon_url} 映射。
    """
    results: dict[str, str | None] = {}
    for name in market_hash_names:
        results[name] = await fetch_icon_url(name)
    return results
