"""FastAPI 依赖注入."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from config import MonitorConfig
from storage.database import Database


def get_db(request: Request) -> Database:
    """依赖注入：数据库实例."""
    return request.app.state.db


def get_config(request: Request) -> MonitorConfig:
    """依赖注入：配置实例."""
    return request.app.state.config


def require_auth(request: Request) -> dict[str, Any]:
    """认证依赖（已禁用，始终通过）.

    登录功能已移除，保留接口签名以避免修改所有路由。
    如需重新启用认证，恢复 JWT 验证逻辑。
    """
    return {"sub": "admin", "role": "admin"}
