"""认证路由（单用户 JWT 登录）."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from config import MonitorConfig
from storage.database import Database
from web.deps import create_access_token, get_config, get_db, require_auth
from web.schemas import LoginRequest, LoginResponse, ChangePasswordRequest

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
    return {
        "access_token": token,
        "token_type": "bearer",
        "requires_password_change": config.is_default_credentials(),
    }


@router.get("/me")
def me(
    payload: dict = Depends(require_auth),
) -> dict:
    """获取当前登录用户信息."""
    return {"username": payload.get("sub", "admin"), "role": "admin"}


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    config: MonitorConfig = Depends(get_config),
    db: Database = Depends(get_db),
    _user: dict = Depends(require_auth),
) -> dict:
    """修改管理员密码（仅支持单用户模式）."""
    if req.current_password != config.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="当前密码错误",
        )
    if len(req.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少 6 位",
        )

    # 持久化到新密码到 system_config 表
    db.set_system_config("admin_password", req.new_password)

    # 如果 jwt_secret 还是默认的，也建议一起改掉
    import secrets
    new_secret = secrets.token_hex(32)
    db.set_system_config("jwt_secret", new_secret)

    return {"message": "密码已更新，请使用新密码重新登录"}
