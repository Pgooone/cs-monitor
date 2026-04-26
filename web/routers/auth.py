"""认证路由（已禁用，保留端点兼容性）."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login() -> dict:
    """登录（已禁用）."""
    return {"access_token": "disabled", "token_type": "bearer", "requires_password_change": False}


@router.get("/me")
def me() -> dict:
    """获取用户信息（已禁用）."""
    return {"username": "admin", "role": "admin"}


@router.post("/change-password")
def change_password() -> dict:
    """修改密码（已禁用）."""
    return {"message": "认证功能已禁用"}
