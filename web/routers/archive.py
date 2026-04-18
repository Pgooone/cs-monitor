"""归档管理路由."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from storage.database import Database
from web.deps import get_db, require_auth

router = APIRouter(prefix="/archive", tags=["archive"])


@router.post("/run")
def run_archive(
    db: Database = Depends(get_db),
    user: dict = Depends(require_auth),
) -> dict[str, Any]:
    """手动触发价格记录归档（90 天以上数据）."""
    result = db.archive_old_price_records(days=90)
    return {
        "message": "归档完成",
        "archived": result["archived"],
        "deleted": result["deleted"],
        "aggregated": result["aggregated"],
    }
