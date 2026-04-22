"""认证路由（单用户 JWT 登录）."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from config import MonitorConfig
from web.deps import create_access_token, get_config
from web.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    req: LoginRequest,
    config: MonitorConfig = Depends(get_config),
) -> dict:
    """用户登录：验证密码并返回 JWT 令牌."""
    if req.password != config.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误",
        )

    token = create_access_token(config)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(
    payload: dict = Depends(require_auth),
) -> dict:
    """获取当前登录用户信息."""
    return {"username": payload.get("sub", "admin"), "role": "admin"}
