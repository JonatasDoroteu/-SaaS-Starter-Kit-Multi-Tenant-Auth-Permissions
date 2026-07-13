from __future__ import annotations

import enum


class Role(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
