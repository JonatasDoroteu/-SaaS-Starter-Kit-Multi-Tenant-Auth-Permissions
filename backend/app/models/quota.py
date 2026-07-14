from __future__ import annotations

from datetime import datetime, timezone

PLAN_LIMITS: dict[str, int | None] = {
    "free": 10,
    "pro": None,  # None = ilimitado
}


def current_period() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")