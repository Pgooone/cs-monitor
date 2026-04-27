"""SteamDT API 客户端封装."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any

import httpx
from loguru import logger

# ───── 异常分层 ─────────────────────────────────────────

class SteamDTError(Exception):
    """SteamDT 调用基类异常."""

    def __init__(self, message: str, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class SteamDTRateLimitError(SteamDTError):
    """HTTP 429 或业务限流错误."""

    def __init__(self, retry_after: float, source: str = "http") -> None:
        super().__init__(
            f"rate limited (source={source}), retry after {retry_after:.1f}s",
            retryable=True,
        )
        self.retry_after = retry_after
        self.source = source  # "http" | "business"


class SteamDTBusinessError(SteamDTError):
    """SteamDT 业务级错误（HTTP 200 + success=false）."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"[errorCode={code}] {message}", retryable=False)
        self.code = code
        self.error_msg = message


# 兼容老代码：原来的 SteamDTAPIError 仍可被 except 捕获
SteamDTAPIError = SteamDTError

# ───── 配置 ────────────────────────────────────────────


@dataclass
class SteamDTConfig:
    """SteamDT 客户端配置."""

    api_key: str
    base_url: str = "https://open.steamdt.com"
    timeout: int = 30
    max_retries: int = 3
    # batch 端点是 1 次/分钟，single 是 60 次/分钟，默认按 batch 防御
    batch_min_interval: float = 60.0


# ───── 节流锁 ──────────────────────────────────────────


class _Throttle:
    """简单的最小间隔节流器（线程安全）."""

    def __init__(self, min_interval: float) -> None:
        self.min_interval = min_interval
        self._last_call = 0.0
        self._lock = threading.Lock()

    def check(self) -> float:
        """返回还需等待的秒数；> 0 表示拒绝调用."""
        with self._lock:
            now = time.monotonic()
            wait = self.min_interval - (now - self._last_call)
            if wait > 0:
                return wait
            self._last_call = now
            return 0.0

    def reset(self) -> None:
        """请求实际失败时回滚（让用户能立刻重试）."""
        with self._lock:
            self._last_call = 0.0


# ───── 主客户端 ────────────────────────────────────────


class SteamDTClient:
    """SteamDT 开放平台 API 客户端（同步版，线程安全）."""

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
        # batch 端点专用节流锁
        self._batch_throttle = _Throttle(config.batch_min_interval)

    # ───── 内部：统一请求处理 ─────

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        last_exc: Exception | None = None

        for attempt in range(1, self.config.max_retries + 1):
            try:
                resp = self._client.request(method, path, **kwargs)
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RequestError) as e:
                last_exc = e
                if attempt < self.config.max_retries:
                    backoff = 2 ** attempt  # 2s, 4s, 8s
                    logger.warning(
                        f"SteamDT 网络错误 (尝试 {attempt}/{self.config.max_retries}): {e}, {backoff}s 后重试"
                    )
                    time.sleep(backoff)
                    continue
                raise SteamDTError(f"network error: {e}") from e

            # 1) 429 限流：读 Retry-After，等待后重试
            if resp.status_code == 429:
                retry_after = self._parse_retry_after(resp)
                logger.warning(
                    f"SteamDT HTTP 429 限流，Retry-After={retry_after}s, attempt={attempt}"
                )
                if attempt < self.config.max_retries:
                    time.sleep(retry_after)
                    continue
                raise SteamDTRateLimitError(retry_after, source="http")

            # 2) 4xx 客户端错误：不重试
            if 400 <= resp.status_code < 500:
                raise SteamDTError(
                    f"HTTP {resp.status_code}: {resp.text[:200]}",
                    retryable=False,
                )

            # 3) 5xx 服务端错误：指数退避
            if resp.status_code >= 500:
                last_exc = SteamDTError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                if attempt < self.config.max_retries:
                    backoff = 2 ** attempt
                    logger.warning(
                        f"SteamDT 5xx (尝试 {attempt}/{self.config.max_retries}), {backoff}s 后重试"
                    )
                    time.sleep(backoff)
                    continue
                raise last_exc  # type: ignore[misc]

            # 4) 200 OK：解析业务错误
            try:
                data = resp.json()
            except ValueError as e:
                raise SteamDTError(f"invalid JSON response: {e}", retryable=False) from e

            if not data.get("success", False):
                code = int(data.get("errorCode", -1))
                msg = str(data.get("errorMsg", "unknown business error"))
                # 业务限流码走 RateLimit 类型
                if code in (4029,) or "限流" in msg or "频繁" in msg or "rate" in msg.lower():
                    raise SteamDTRateLimitError(retry_after=60.0, source="business")
                raise SteamDTBusinessError(code=code, message=msg)

            return data

        raise SteamDTError(f"retries exhausted: {last_exc}") from last_exc

    @staticmethod
    def _parse_retry_after(resp: httpx.Response) -> float:
        """读取 Retry-After 头，秒数或 HTTP date 格式都支持."""
        ra = resp.headers.get("Retry-After")
        if not ra:
            return 60.0
        try:
            return max(1.0, float(ra))
        except ValueError:
            return 60.0

    # ───── 公开 API ─────

    def get_items_batch(
        self, market_hash_names: list[str], use_throttle: bool = True
    ) -> dict[str, Any]:
        """批量查询饰品价格（**1 次/分钟限制**）.

        Args:
            market_hash_names: 饰品名称列表，1-100 个.
            use_throttle: 是否使用客户端侧节流锁（推荐 True）.
                定时采集场景（monitor.py）周期 >= 60s，可设 False.
                手动刷新场景（refresh API）必须 True.
        """
        if not market_hash_names:
            return {"success": True, "data": []}
        if len(market_hash_names) > 100:
            raise ValueError(
                f"market_hash_names 最多支持 100 个，当前 {len(market_hash_names)} 个"
            )

        if use_throttle:
            wait = self._batch_throttle.check()
            if wait > 0:
                raise SteamDTRateLimitError(retry_after=wait, source="business")

        try:
            return self._request(
                "POST",
                "/open/cs2/v1/price/batch",
                json={"marketHashNames": market_hash_names},
            )
        except Exception:
            if use_throttle:
                self._batch_throttle.reset()
            raise

    def get_item_price_single(self, market_hash_name: str) -> dict[str, Any]:
        """单条查询（60 次/分钟），用于详情页."""
        return self._request(
            "GET",
            "/open/cs2/v1/price/single",
            params={"marketHashName": market_hash_name},
        )

    def get_7day_average(self, market_hash_name: str) -> dict[str, Any]:
        """通过 MarketHashName 查询所有平台近 7 天均价."""
        return self._request(
            "GET",
            "/open/cs2/v1/price/avg",
            params={"marketHashName": market_hash_name},
        )

    def get_all_items(self) -> dict[str, Any]:
        """获取 Steam 饰品基础信息（每天只能调用 1 次）."""
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
        """
        payload: dict[str, Any] = {
            "marketHashName": market_hash_name,
            "type": kline_type,
            "platform": platform,
        }
        if special_style is not None:
            payload["specialStyle"] = special_style
        return self._request("POST", "/open/cs2/item/v1/kline", json=payload)

    # ───── 上下文管理 ─────

    def close(self) -> None:
        """关闭 HTTP 客户端."""
        self._client.close()

    def __enter__(self) -> SteamDTClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
